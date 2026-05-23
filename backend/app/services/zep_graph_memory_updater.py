"""
Zepgraphupdate
simulationAgentupdateZepgraph
"""

import os
import time
import threading
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from queue import Queue, Empty

from zep_cloud.client import Zep

from ..config import Config
from ..utils.logger import get_logger
from ..utils.locale import get_locale, set_locale

logger = get_logger('mirofish.zep_graph_memory_updater')


@dataclass
class AgentActivity:
    """Agent"""
    platform: str # twitter / reddit
    agent_id: int
    agent_name: str
    action_type: str # CREATE_POST, LIKE_POST, etc.
    action_args: Dict[str, Any]
    round_num: int
    timestamp: str
    
    def to_episode_text(self) -> str:
        """
        Zep
        
        ，Zep
        simulation，graphupdate
        """
        # type
        action_descriptions = {
            "CREATE_POST": self._describe_create_post,
            "LIKE_POST": self._describe_like_post,
            "DISLIKE_POST": self._describe_dislike_post,
            "REPOST": self._describe_repost,
            "QUOTE_POST": self._describe_quote_post,
            "FOLLOW": self._describe_follow,
            "CREATE_COMMENT": self._describe_create_comment,
            "LIKE_COMMENT": self._describe_like_comment,
            "DISLIKE_COMMENT": self._describe_dislike_comment,
            "SEARCH_POSTS": self._describe_search,
            "SEARCH_USER": self._describe_search_user,
            "MUTE": self._describe_mute,
        }
        
        describe_func = action_descriptions.get(self.action_type, self._describe_generic)
        description = describe_func()
        
        # return "agentname: " ，simulation
        return f"{self.agent_name}: {description}"
    
    def _describe_create_post(self) -> str:
        content = self.action_args.get("content", "")
        if content:
            return f"：「{content}」"
        return ""
    
    def _describe_like_post(self) -> str:
        """ - """
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if post_content and post_author:
            return f"{post_author}：「{post_content}」"
        elif post_content:
            return f"：「{post_content}」"
        elif post_author:
            return f"{post_author}"
        return ""
    
    def _describe_dislike_post(self) -> str:
        """ - """
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if post_content and post_author:
            return f"{post_author}：「{post_content}」"
        elif post_content:
            return f"：「{post_content}」"
        elif post_author:
            return f"{post_author}"
        return ""
    
    def _describe_repost(self) -> str:
        """ - content"""
        original_content = self.action_args.get("original_content", "")
        original_author = self.action_args.get("original_author_name", "")
        
        if original_content and original_author:
            return f"{original_author}：「{original_content}」"
        elif original_content:
            return f"：「{original_content}」"
        elif original_author:
            return f"{original_author}"
        return ""
    
    def _describe_quote_post(self) -> str:
        """ - content、"""
        original_content = self.action_args.get("original_content", "")
        original_author = self.action_args.get("original_author_name", "")
        quote_content = self.action_args.get("quote_content", "") or self.action_args.get("content", "")
        
        base = ""
        if original_content and original_author:
            base = f"{original_author}「{original_content}」"
        elif original_content:
            base = f"「{original_content}」"
        elif original_author:
            base = f"{original_author}"
        else:
            base = ""
        
        if quote_content:
            base += f"，：「{quote_content}」"
        return base
    
    def _describe_follow(self) -> str:
        """ - name"""
        target_user_name = self.action_args.get("target_user_name", "")
        
        if target_user_name:
            return f"「{target_user_name}」"
        return ""
    
    def _describe_create_comment(self) -> str:
        """ - content"""
        content = self.action_args.get("content", "")
        post_content = self.action_args.get("post_content", "")
        post_author = self.action_args.get("post_author_name", "")
        
        if content:
            if post_content and post_author:
                return f"{post_author}「{post_content}」：「{content}」"
            elif post_content:
                return f"「{post_content}」：「{content}」"
            elif post_author:
                return f"{post_author}：「{content}」"
            return f"：「{content}」"
        return ""
    
    def _describe_like_comment(self) -> str:
        """ - content"""
        comment_content = self.action_args.get("comment_content", "")
        comment_author = self.action_args.get("comment_author_name", "")
        
        if comment_content and comment_author:
            return f"{comment_author}：「{comment_content}」"
        elif comment_content:
            return f"：「{comment_content}」"
        elif comment_author:
            return f"{comment_author}"
        return ""
    
    def _describe_dislike_comment(self) -> str:
        """ - content"""
        comment_content = self.action_args.get("comment_content", "")
        comment_author = self.action_args.get("comment_author_name", "")
        
        if comment_content and comment_author:
            return f"{comment_author}：「{comment_content}」"
        elif comment_content:
            return f"：「{comment_content}」"
        elif comment_author:
            return f"{comment_author}"
        return ""
    
    def _describe_search(self) -> str:
        """ - """
        query = self.action_args.get("query", "") or self.action_args.get("keyword", "")
        return f"「{query}」" if query else ""
    
    def _describe_search_user(self) -> str:
        """ - """
        query = self.action_args.get("query", "") or self.action_args.get("username", "")
        return f"「{query}」" if query else ""
    
    def _describe_mute(self) -> str:
        """ - name"""
        target_user_name = self.action_args.get("target_user_name", "")
        
        if target_user_name:
            return f"「{target_user_name}」"
        return ""
    
    def _describe_generic(self) -> str:
        # type，
        return f"{self.action_type}"


class ZepGraphMemoryUpdater:
    """
    Zepgraphupdate
    
    simulationactionsLog files，agentupdateZepgraph。
    platform，BATCH_SIZEZep。
    
    updateZep，action_args：
    - /
    - /
    - /
    - /
    """
    
    # （platform）
    BATCH_SIZE = 5
    
    # platformname（）
    PLATFORM_DISPLAY_NAMES = {
        'twitter': '1',
        'reddit': '2',
    }
    
    # （seconds），request
    SEND_INTERVAL = 0.5
    
    # configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2 # seconds
    
    def __init__(self, graph_id: str, api_key: Optional[str] = None):
        """
        initializeupdate
        
        Args:
            graph_id: ZepgraphID
            api_key: Zep API Key（optional，defaultconfigurationread）
        """
        self.graph_id = graph_id
        self.api_key = api_key or Config.ZEP_API_KEY
        
        if not self.api_key:
            raise ValueError("ZEP_API_KEYnot configured")
        
        self.client = Zep(api_key=self.api_key)
        
        # 
        self._activity_queue: Queue = Queue()
        
        # platform（platformBATCH_SIZE）
        self._platform_buffers: Dict[str, List[AgentActivity]] = {
            'twitter': [],
            'reddit': [],
        }
        self._buffer_lock = threading.Lock()
        
        # 
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        # statistics
        self._total_activities = 0 # 
        self._total_sent = 0 # successZep
        self._total_items_sent = 0 # successZep
        self._failed_count = 0 # failed
        self._skipped_count = 0 # （DO_NOTHING）
        
        logger.info(f"ZepGraphMemoryUpdater initialize: graph_id={graph_id}, batch_size={self.BATCH_SIZE}")
    
    def _get_platform_display_name(self, platform: str) -> str:
        """getplatformname"""
        return self.PLATFORM_DISPLAY_NAMES.get(platform.lower(), platform)
    
    def start(self):
        """start"""
        if self._running:
            return

        # Capture locale before spawning background thread
        current_locale = get_locale()

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            args=(current_locale,),
            daemon=True,
            name=f"ZepMemoryUpdater-{self.graph_id[:8]}"
        )
        self._worker_thread.start()
        logger.info(f"ZepGraphMemoryUpdater start: graph_id={self.graph_id}")
    
    def stop(self):
        """stop"""
        self._running = False
        
        # 
        self._flush_remaining()
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=10)
        
        logger.info(f"ZepGraphMemoryUpdater stop: graph_id={self.graph_id}, "
                   f"total_activities={self._total_activities}, "
                   f"batches_sent={self._total_sent}, "
                   f"items_sent={self._total_items_sent}, "
                   f"failed={self._failed_count}, "
                   f"skipped={self._skipped_count}")
    
    def add_activity(self, activity: AgentActivity):
        """
        agent
        
        ，：
        - CREATE_POST（）
        - CREATE_COMMENT（）
        - QUOTE_POST（）
        - SEARCH_POSTS（）
        - SEARCH_USER（）
        - LIKE_POST/DISLIKE_POST（/）
        - REPOST（）
        - FOLLOW（）
        - MUTE（）
        - LIKE_COMMENT/DISLIKE_COMMENT（/）
        
        action_args（、）。
        
        Args:
            activity: Agent
        """
        # DO_NOTHINGtype
        if activity.action_type == "DO_NOTHING":
            self._skipped_count += 1
            return
        
        self._activity_queue.put(activity)
        self._total_activities += 1
        logger.debug(f"Zep: {activity.agent_name} - {activity.action_type}")
    
    def add_activity_from_dict(self, data: Dict[str, Any], platform: str):
        """
        data
        
        Args:
            data: actions.jsonldata
            platform: platformname (twitter/reddit)
        """
        # type
        if "event_type" in data:
            return
        
        activity = AgentActivity(
            platform=platform,
            agent_id=data.get("agent_id", 0),
            agent_name=data.get("agent_name", ""),
            action_type=data.get("action_type", ""),
            action_args=data.get("action_args", {}),
            round_num=data.get("round", 0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
        )
        
        self.add_activity(activity)
    
    def _worker_loop(self, locale: str = 'zh'):
        """ - platformZep"""
        set_locale(locale)
        while self._running or not self._activity_queue.empty():
            try:
                # get（timeout1seconds）
                try:
                    activity = self._activity_queue.get(timeout=1)
                    
                    # platform
                    platform = activity.platform.lower()
                    with self._buffer_lock:
                        if platform not in self._platform_buffers:
                            self._platform_buffers[platform] = []
                        self._platform_buffers[platform].append(activity)
                        
                        # platform
                        if len(self._platform_buffers[platform]) >= self.BATCH_SIZE:
                            batch = self._platform_buffers[platform][:self.BATCH_SIZE]
                            self._platform_buffers[platform] = self._platform_buffers[platform][self.BATCH_SIZE:]
                            # 
                            self._send_batch_activities(batch, platform)
                            # ，request
                            time.sleep(self.SEND_INTERVAL)
                    
                except Empty:
                    pass
                    
            except Exception as e:
                logger.error(f": {e}")
                time.sleep(1)
    
    def _send_batch_activities(self, activities: List[AgentActivity], platform: str):
        """
        Zepgraph（）
        
        Args:
            activities: Agentlist
            platform: platformname
        """
        if not activities:
            return
        
        # ，
        episode_texts = [activity.to_episode_text() for activity in activities]
        combined_text = "\n".join(episode_texts)
        
        # 
        for attempt in range(self.MAX_RETRIES):
            try:
                self.client.graph.add(
                    graph_id=self.graph_id,
                    type="text",
                    data=combined_text
                )
                
                self._total_sent += 1
                self._total_items_sent += len(activities)
                display_name = self._get_platform_display_name(platform)
                logger.info(f"success {len(activities)} {display_name}graph {self.graph_id}")
                logger.debug(f"content: {combined_text[:200]}...")
                return
                
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    logger.warning(f"Zepfailed ( {attempt + 1}/{self.MAX_RETRIES}): {e}")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"Zepfailed，{self.MAX_RETRIES}: {e}")
                    self._failed_count += 1
    
    def _flush_remaining(self):
        """"""
        # ，
        while not self._activity_queue.empty():
            try:
                activity = self._activity_queue.get_nowait()
                platform = activity.platform.lower()
                with self._buffer_lock:
                    if platform not in self._platform_buffers:
                        self._platform_buffers[platform] = []
                    self._platform_buffers[platform].append(activity)
            except Empty:
                break
        
        # platform（BATCH_SIZE）
        with self._buffer_lock:
            for platform, buffer in self._platform_buffers.items():
                if buffer:
                    display_name = self._get_platform_display_name(platform)
                    logger.info(f"{display_name}platform {len(buffer)} ")
                    self._send_batch_activities(buffer, platform)
            # 
            for platform in self._platform_buffers:
                self._platform_buffers[platform] = []
    
    def get_stats(self) -> Dict[str, Any]:
        """getstatistics"""
        with self._buffer_lock:
            buffer_sizes = {p: len(b) for p, b in self._platform_buffers.items()}
        
        return {
            "graph_id": self.graph_id,
            "batch_size": self.BATCH_SIZE,
            "total_activities": self._total_activities, # 
            "batches_sent": self._total_sent, # success
            "items_sent": self._total_items_sent, # success
            "failed_count": self._failed_count, # failed
            "skipped_count": self._skipped_count, # （DO_NOTHING）
            "queue_size": self._activity_queue.qsize(),
            "buffer_sizes": buffer_sizes, # platform
            "running": self._running,
        }


class ZepGraphMemoryManager:
    """
    simulationZepgraphupdate
    
    simulationupdate
    """
    
    _updaters: Dict[str, ZepGraphMemoryUpdater] = {}
    _lock = threading.Lock()
    
    @classmethod
    def create_updater(cls, simulation_id: str, graph_id: str) -> ZepGraphMemoryUpdater:
        """
        simulationcreategraphupdate
        
        Args:
            simulation_id: simulationID
            graph_id: ZepgraphID
            
        Returns:
            ZepGraphMemoryUpdater
        """
        with cls._lock:
            # ，stop
            if simulation_id in cls._updaters:
                cls._updaters[simulation_id].stop()
            
            updater = ZepGraphMemoryUpdater(graph_id)
            updater.start()
            cls._updaters[simulation_id] = updater
            
            logger.info(f"creategraphupdate: simulation_id={simulation_id}, graph_id={graph_id}")
            return updater
    
    @classmethod
    def get_updater(cls, simulation_id: str) -> Optional[ZepGraphMemoryUpdater]:
        """getsimulationupdate"""
        return cls._updaters.get(simulation_id)
    
    @classmethod
    def stop_updater(cls, simulation_id: str):
        """stopsimulationupdate"""
        with cls._lock:
            if simulation_id in cls._updaters:
                cls._updaters[simulation_id].stop()
                del cls._updaters[simulation_id]
                logger.info(f"stopgraphupdate: simulation_id={simulation_id}")
    
    # stop_all 
    _stop_all_done = False
    
    @classmethod
    def stop_all(cls):
        """stopupdate"""
        # 
        if cls._stop_all_done:
            return
        cls._stop_all_done = True
        
        with cls._lock:
            if cls._updaters:
                for simulation_id, updater in list(cls._updaters.items()):
                    try:
                        updater.stop()
                    except Exception as e:
                        logger.error(f"stopupdatefailed: simulation_id={simulation_id}, error={e}")
                cls._updaters.clear()
            logger.info("stopgraphupdate")
    
    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict[str, Any]]:
        """getupdatestatistics"""
        return {
            sim_id: updater.get_stats() 
            for sim_id, updater in cls._updaters.items()
        }
