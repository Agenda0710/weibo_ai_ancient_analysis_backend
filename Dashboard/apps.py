from django.apps import AppConfig
import threading
import logging

logger = logging.getLogger(__name__)

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dashboard'

    def ready(self):
        """
        当Django启动时自动调用此方法
        """
        # 只在主线程中启动工作线程，避免在运行迁移等命令时重复启动
        try:
            import os
            if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('RUN_WORKER') == 'true':
                self.start_sentiment_analysis_worker()
        except Exception as e:
            logger.error(f"Failed to start worker thread: {str(e)}")

    def start_sentiment_analysis_worker(self):
        """
        启动情感分析工作线程
        """
        from .worker import sentiment_analysis_worker

        # 检查是否已经启动过工作线程
        if not hasattr(self, '_worker_thread_started'):
            logger.info("Starting sentiment analysis worker thread...")
            worker_thread = threading.Thread(
                target=sentiment_analysis_worker,
                name="SentimentAnalysisWorker",
                daemon=True
            )
            worker_thread.start()
            self._worker_thread_started = True
            logger.info("Sentiment analysis worker thread started successfully")