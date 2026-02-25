"""
FeedbackAgent — Runs 24 hours after publication to collect metrics,
analyze sentiment, compute engagement scores, generate embeddings,
and feed data back into DSPy optimizer.
"""

import json
from datetime import datetime, timezone

import requests
import structlog

from core.config import get_settings
from core.celery_app import celery_app
from core.supabase import get_supabase_client

logger = structlog.get_logger()

HF_SENTIMENT_URL = (
    "https://api-inference.huggingface.co/models/"
    "cardiffnlp/twitter-roberta-base-sentiment-latest"
)
HF_EMBEDDING_URL = (
    "https://api-inference.huggingface.co/models/"
    "sentence-transformers/all-MiniLM-L6-v2"
)

ENGAGEMENT_THRESHOLD = 0.05  # Score above this triggers DSPy training


def schedule_feedback_collection(post_id: str, delay_hours: int = 24):
    """Schedule feedback collection for a post, 24 hours after publication."""
    celery_app.send_task(
        "agents.feedback_agent.collect_feedback_task",
        args=[post_id],
        countdown=delay_hours * 3600,
    )
    logger.info("Feedback collection scheduled", post_id=post_id, delay_hours=delay_hours)


class FeedbackAgent:
    def __init__(self):
        self.settings = get_settings()
        self.hf_headers = {"Authorization": f"Bearer {self.settings.hf_token}"}

    async def run(self, post_id: str) -> dict:
        """
        Full feedback loop:
        1. Fetch metrics from Ayrshare
        2. Run sentiment analysis on comments
        3. Compute engagement score
        4. Store metrics in database
        5. Generate and store content embedding
        6. Update DSPy optimizer if score > threshold
        """
        supabase = get_supabase_client()

        # Fetch post data
        post = supabase.table("posts").select("*").eq("id", post_id).single().execute()
        if not post.data:
            logger.error("Post not found for feedback", post_id=post_id)
            return {"error": "Post not found"}

        post_data = post.data

        # Step 1: Fetch metrics from Ayrshare
        raw_metrics = self._fetch_ayrshare_metrics(post_data.get("external_post_id"))

        # Step 2: Analyze sentiment on comments
        comments = raw_metrics.get("comments_text", [])
        sentiment = self._analyze_sentiment(comments) if comments else {
            "positive": 0, "neutral": 0, "negative": 0, "score": 0
        }

        # Step 3: Compute engagement score
        likes = raw_metrics.get("likes", 0)
        comments_count = raw_metrics.get("comments", 0)
        shares = raw_metrics.get("shares", 0)
        reach = raw_metrics.get("reach", 1)

        engagement_score = (likes + 3 * comments_count + 5 * shares) / max(reach, 1)

        # Step 4: Store metrics
        metrics_record = {
            "post_id": post_id,
            "likes": likes,
            "comments": comments_count,
            "shares": shares,
            "reach": reach,
            "impressions": raw_metrics.get("impressions", 0),
            "clicks": raw_metrics.get("clicks", 0),
            "sentiment_score": sentiment["score"],
            "sentiment_breakdown": {
                "positive": sentiment["positive"],
                "neutral": sentiment["neutral"],
                "negative": sentiment["negative"],
            },
        }

        supabase.table("metrics").insert(metrics_record).execute()

        # Update engagement score on the post
        supabase.table("posts").update({
            "engagement_score": engagement_score,
        }).eq("id", post_id).execute()

        # Step 5: Generate and store embedding
        embedding = self._generate_embedding(post_data["content"])
        if embedding:
            supabase.table("posts").update({
                "embedding": embedding,
            }).eq("id", post_id).execute()

        # Step 6: Update DSPy optimizer if score is good enough
        if engagement_score > ENGAGEMENT_THRESHOLD:
            self._update_dspy_optimizer(post_data, engagement_score)

        logger.info(
            "Feedback collected",
            post_id=post_id,
            engagement_score=round(engagement_score, 4),
            sentiment_score=round(sentiment["score"], 3),
        )

        return {
            "post_id": post_id,
            "engagement_score": engagement_score,
            "sentiment": sentiment,
            "metrics": metrics_record,
        }

    def _fetch_ayrshare_metrics(self, external_post_id: str | None) -> dict:
        """Fetch engagement metrics from Ayrshare API."""
        if not external_post_id or not self.settings.ayrshare_api_key:
            logger.warning("Cannot fetch metrics: no external ID or API key")
            return {}

        try:
            response = requests.get(
                "https://app.ayrshare.com/api/analytics/post",
                headers={
                    "Authorization": f"Bearer {self.settings.ayrshare_api_key}",
                    "Content-Type": "application/json",
                },
                params={"id": external_post_id},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                return {
                    "likes": analytics.get("likes", 0),
                    "comments": analytics.get("comments", 0),
                    "shares": analytics.get("shares", 0) + analytics.get("reposts", 0),
                    "reach": analytics.get("reach", 0) or analytics.get("impressions", 0),
                    "impressions": analytics.get("impressions", 0),
                    "clicks": analytics.get("clicks", 0),
                    "comments_text": analytics.get("commentsList", []),
                }
            else:
                logger.warning("Ayrshare analytics failed", status=response.status_code)
                return {}

        except Exception as e:
            logger.error("Failed to fetch Ayrshare metrics", error=str(e))
            return {}

    def _analyze_sentiment(self, comments: list[str]) -> dict:
        """Analyze sentiment of comments using Twitter-RoBERTa on HuggingFace."""
        if not comments or not self.settings.hf_token:
            return {"positive": 0, "neutral": 0, "negative": 0, "score": 0}

        try:
            # Batch comments (HF API accepts list input)
            texts = [c[:512] for c in comments[:20]]  # Limit to 20 comments, 512 chars each

            response = requests.post(
                HF_SENTIMENT_URL,
                headers=self.hf_headers,
                json={"inputs": texts},
                timeout=30,
            )

            if response.status_code != 200:
                logger.warning("Sentiment API failed", status=response.status_code)
                return {"positive": 0, "neutral": 0, "negative": 0, "score": 0}

            results = response.json()

            # Aggregate sentiment
            total = len(results)
            positive = 0
            neutral = 0
            negative = 0

            for result in results:
                if isinstance(result, list):
                    # Each result is a list of label scores
                    label_scores = {r["label"]: r["score"] for r in result}
                    best_label = max(label_scores, key=label_scores.get)
                    if "positive" in best_label.lower():
                        positive += 1
                    elif "negative" in best_label.lower():
                        negative += 1
                    else:
                        neutral += 1

            score = (positive - negative) / max(total, 1)

            return {
                "positive": positive / max(total, 1),
                "neutral": neutral / max(total, 1),
                "negative": negative / max(total, 1),
                "score": score,
            }

        except Exception as e:
            logger.error("Sentiment analysis failed", error=str(e))
            return {"positive": 0, "neutral": 0, "negative": 0, "score": 0}

    def _generate_embedding(self, content: str) -> list[float] | None:
        """Generate MiniLM-L6-v2 embedding via HuggingFace Inference API."""
        if not self.settings.hf_token:
            return None

        try:
            response = requests.post(
                HF_EMBEDDING_URL,
                headers=self.hf_headers,
                json={"inputs": content[:512]},
                timeout=30,
            )

            if response.status_code == 200:
                embedding = response.json()
                # API returns list of floats for single input
                if isinstance(embedding, list) and len(embedding) == 384:
                    return embedding
                elif isinstance(embedding, list) and isinstance(embedding[0], list):
                    return embedding[0]
                logger.warning("Unexpected embedding format", type=type(embedding))
                return None
            else:
                logger.warning("Embedding API failed", status=response.status_code)
                return None

        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            return None

    def _update_dspy_optimizer(self, post_data: dict, score: float) -> None:
        """Add successful post as DSPy training example and recompile if enough examples."""
        try:
            supabase = get_supabase_client()
            brand_id = post_data["brand_id"]

            # Get current DSPy state
            state = (
                supabase.table("dspy_state")
                .select("*")
                .eq("brand_id", brand_id)
                .order("version", desc=True)
                .limit(1)
                .execute()
            )

            # Build training example
            example = {
                "content": post_data["content"],
                "hook": post_data.get("hook", ""),
                "platform": post_data["platform"],
                "trend_angle": post_data.get("trend_angle", ""),
                "engagement_score": score,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            if state.data:
                # Append to existing examples
                existing = state.data[0]
                examples = existing.get("training_examples", [])
                examples.append(example)

                supabase.table("dspy_state").update({
                    "training_examples": examples,
                    "score": score,
                }).eq("id", existing["id"]).execute()

                # Trigger recompilation if we have enough examples
                if len(examples) >= 10 and len(examples) % 5 == 0:
                    self._recompile_dspy(brand_id, examples)
            else:
                # Create initial state
                supabase.table("dspy_state").insert({
                    "brand_id": brand_id,
                    "compiled_state": {},
                    "training_examples": [example],
                    "score": score,
                    "version": 1,
                }).execute()

            logger.info(
                "DSPy training example added",
                brand_id=brand_id,
                score=round(score, 4),
            )

        except Exception as e:
            logger.error("DSPy update failed", error=str(e))

    def _recompile_dspy(self, brand_id: str, examples: list[dict]) -> None:
        """Recompile DSPy optimizer with updated training examples."""
        try:
            import dspy
            from agents.content_agent import GeneratePost

            settings = get_settings()
            lm = dspy.LM(
                model="gemini/gemini-2.0-flash",
                api_key=settings.gemini_api_key,
            )
            dspy.configure(lm=lm)

            # Build DSPy examples
            trainset = []
            for ex in examples:
                trainset.append(
                    dspy.Example(
                        trend_angle=ex.get("trend_angle", ""),
                        brand_voice=f"Platform: {ex.get('platform', '')}",
                        platform=ex.get("platform", "linkedin"),
                        past_winners="",
                        caption=ex.get("content", ""),
                        hook=ex.get("hook", ""),
                    ).with_inputs("trend_angle", "brand_voice", "platform", "past_winners")
                )

            if len(trainset) < 5:
                return

            # Run BootstrapFewShot
            def engagement_metric(example, pred, trace=None):
                score = next(
                    (e["engagement_score"] for e in examples if e["content"] == pred.caption),
                    0.03,
                )
                return score > ENGAGEMENT_THRESHOLD

            optimizer = dspy.BootstrapFewShot(
                metric=engagement_metric,
                max_bootstrapped_demos=3,
                max_labeled_demos=5,
            )

            generator = dspy.ChainOfThought(GeneratePost)
            compiled = optimizer.compile(generator, trainset=trainset)

            # Save compiled state
            compiled_state = compiled.dump_state()
            supabase = get_supabase_client()
            supabase.table("dspy_state").insert({
                "brand_id": brand_id,
                "compiled_state": compiled_state,
                "training_examples": examples,
                "score": max(e["engagement_score"] for e in examples),
                "version": len(examples),
            }).execute()

            logger.info(
                "DSPy recompiled",
                brand_id=brand_id,
                examples_count=len(examples),
            )

        except Exception as e:
            logger.error("DSPy recompilation failed", error=str(e))


@celery_app.task(
    name="agents.feedback_agent.collect_feedback_task",
    bind=True,
    max_retries=3,
)
def collect_feedback_task(self, post_id: str):
    """Celery task: collect feedback 24 hours after publication."""
    import asyncio

    try:
        agent = FeedbackAgent()
        result = asyncio.get_event_loop().run_until_complete(agent.run(post_id))
        return result
    except Exception as e:
        logger.error("Feedback collection task failed", post_id=post_id, error=str(e))
        raise self.retry(exc=e, countdown=3600)  # Retry in 1 hour
