"""
Database Models and Connection
=============================

This module handles database connection and models for storing scraped data.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from loguru import logger

# Database configuration
DATABASE_URL = "postgresql://zara:zara123@localhost:5432/zara_scraper"

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


class ScrapeSession(Base):
    """Model for storing scrape sessions"""
    __tablename__ = "scrape_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    url = Column(String(500), nullable=False)
    locale = Column(String(10), default="en-US")
    success = Column(Boolean, default=False)
    html_file = Column(String(500))
    screenshot_file = Column(String(500))
    title = Column(String(200))
    error_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScrapedProduct(Base):
    """Model for storing scraped products"""
    __tablename__ = "scraped_products"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    product_name = Column(String(200))
    product_url = Column(String(500))
    category = Column(String(100))
    price = Column(String(50))
    image_url = Column(String(500))
    description = Column(Text)
    popularity_score = Column(Float, default=0.0)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScrapedBanner(Base):
    """Model for storing scraped banners"""
    __tablename__ = "scraped_banners"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    banner_text = Column(String(200))
    banner_url = Column(String(500))
    banner_type = Column(String(50))  # hero, category, promotion
    position = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScrapeError(Base):
    """Model for storing scrape errors"""
    __tablename__ = "scrape_errors"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True)
    error_type = Column(String(100))
    error_message = Column(Text)
    error_timestamp = Column(DateTime, default=datetime.utcnow)
    retry_count = Column(Integer, default=0)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Database manager for handling operations"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            return False
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def save_scrape_session(self, scrape_data: Dict) -> Optional[int]:
        """Save scrape session to database"""
        try:
            session = self.get_session()
            
            db_session = ScrapeSession(
                timestamp=datetime.fromisoformat(scrape_data["timestamp"].replace("_", " ")),
                url=scrape_data["url"],
                locale=scrape_data.get("locale", "en-US"),
                success=scrape_data["success"],
                html_file=scrape_data.get("html_file"),
                screenshot_file=scrape_data.get("screenshot_file"),
                title=scrape_data.get("title"),
                error_count=len(scrape_data.get("errors", [])),
                retry_count=scrape_data.get("retries", 0)
            )
            
            session.add(db_session)
            session.commit()
            session.refresh(db_session)
            
            logger.info(f"Saved scrape session with ID: {db_session.id}")
            return db_session.id
            
        except Exception as e:
            logger.error(f"Failed to save scrape session: {str(e)}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def save_scraped_banners(self, session_id: int, banners: List[Dict]) -> bool:
        """Save scraped banners to database"""
        try:
            db_session = self.get_session()
            
            for banner in banners:
                db_banner = ScrapedBanner(
                    session_id=session_id,
                    banner_text=banner.get("text", ""),
                    banner_url=banner.get("href", ""),
                    banner_type=banner.get("type", "unknown"),
                    position=banner.get("index", 0)
                )
                db_session.add(db_banner)
            
            db_session.commit()
            logger.info(f"Saved {len(banners)} banners for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save banners: {str(e)}")
            db_session.rollback()
            return False
        finally:
            db_session.close()
    
    def save_scrape_errors(self, session_id: int, errors: List[str]) -> bool:
        """Save scrape errors to database"""
        try:
            db_session = self.get_session()
            
            for error in errors:
                db_error = ScrapeError(
                    session_id=session_id,
                    error_type="scraping_error",
                    error_message=error
                )
                db_session.add(db_error)
            
            db_session.commit()
            logger.info(f"Saved {len(errors)} errors for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save errors: {str(e)}")
            db_session.rollback()
            return False
        finally:
            db_session.close()
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent scrape sessions"""
        try:
            session = self.get_session()
            
            db_sessions = session.query(ScrapeSession).order_by(
                ScrapeSession.timestamp.desc()
            ).limit(limit).all()
            
            sessions = []
            for db_session in db_sessions:
                sessions.append({
                    "id": db_session.id,
                    "timestamp": db_session.timestamp.isoformat(),
                    "url": db_session.url,
                    "success": db_session.success,
                    "title": db_session.title,
                    "error_count": db_session.error_count,
                    "retry_count": db_session.retry_count
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get recent sessions: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_session_by_id(self, session_id: int) -> Optional[Dict]:
        """Get scrape session by ID"""
        try:
            session = self.get_session()
            
            db_session = session.query(ScrapeSession).filter(
                ScrapeSession.id == session_id
            ).first()
            
            if db_session:
                return {
                    "id": db_session.id,
                    "timestamp": db_session.timestamp.isoformat(),
                    "url": db_session.url,
                    "success": db_session.success,
                    "title": db_session.title,
                    "html_file": db_session.html_file,
                    "screenshot_file": db_session.screenshot_file,
                    "error_count": db_session.error_count,
                    "retry_count": db_session.retry_count
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_banners_by_session(self, session_id: int) -> List[Dict]:
        """Get banners for a specific session"""
        try:
            session = self.get_session()
            
            db_banners = session.query(ScrapedBanner).filter(
                ScrapedBanner.session_id == session_id
            ).order_by(ScrapedBanner.position).all()
            
            banners = []
            for db_banner in db_banners:
                banners.append({
                    "id": db_banner.id,
                    "text": db_banner.banner_text,
                    "url": db_banner.banner_url,
                    "type": db_banner.banner_type,
                    "position": db_banner.position,
                    "is_active": db_banner.is_active
                })
            
            return banners
            
        except Exception as e:
            logger.error(f"Failed to get banners for session {session_id}: {str(e)}")
            return []
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()


def init_database():
    """Initialize database tables"""
    return db_manager.create_tables()


def save_scrape_results(scrape_data: Dict) -> Optional[int]:
    """Save complete scrape results to database"""
    try:
        # Save main session
        session_id = db_manager.save_scrape_session(scrape_data)
        
        if session_id:
            # Save banners if any
            if scrape_data.get("banners"):
                db_manager.save_scraped_banners(session_id, scrape_data["banners"])
            
            # Save errors if any
            if scrape_data.get("errors"):
                db_manager.save_scrape_errors(session_id, scrape_data["errors"])
            
            logger.info(f"Saved complete scrape results for session {session_id}")
            return session_id
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to save scrape results: {str(e)}")
        return None


def get_scrape_history(limit: int = 10) -> List[Dict]:
    """Get scrape history"""
    return db_manager.get_recent_sessions(limit)


def get_scrape_details(session_id: int) -> Optional[Dict]:
    """Get detailed scrape information"""
    session_data = db_manager.get_session_by_id(session_id)
    
    if session_data:
        banners = db_manager.get_banners_by_session(session_id)
        session_data["banners"] = banners
        return session_data
    
    return None


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    
    if init_database():
        print("✅ Database initialized successfully")
        
        # Test saving a sample session
        sample_data = {
            "timestamp": "20250828_203225",
            "url": "https://www.zara.com/",
            "success": False,
            "errors": ["Access denied"],
            "retries": 3
        }
        
        session_id = save_scrape_results(sample_data)
        if session_id:
            print(f"✅ Sample session saved with ID: {session_id}")
            
            # Test retrieving data
            history = get_scrape_history(5)
            print(f"✅ Retrieved {len(history)} recent sessions")
            
            details = get_scrape_details(session_id)
            if details:
                print(f"✅ Retrieved session details for ID: {session_id}")
        
    else:
        print("❌ Database initialization failed")

