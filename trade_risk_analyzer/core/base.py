"""
Base Classes and Interfaces for Extensibility
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    """Risk level enumeration"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TradeType(Enum):
    """Trade type enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class PatternType(Enum):
    """Pattern type enumeration"""
    WASH_TRADING = "WASH_TRADING"
    PUMP_AND_DUMP = "PUMP_AND_DUMP"
    LAYERING = "LAYERING"
    SPOOFING = "SPOOFING"
    HFT_MANIPULATION = "HFT_MANIPULATION"
    GENERAL_ANOMALY = "GENERAL_ANOMALY"


@dataclass
class Trade:
    """Trade data model"""
    trade_id: str
    user_id: str
    timestamp: datetime
    symbol: str
    price: float
    volume: float
    trade_type: TradeType
    order_id: Optional[str] = None


@dataclass
class ValidationError:
    """Validation error details"""
    field: str
    message: str
    value: Any


@dataclass
class ValidationResult:
    """Validation result"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]
    valid_records: int
    invalid_records: int


@dataclass
class Alert:
    """Risk alert"""
    alert_id: str
    timestamp: datetime
    user_id: str
    trade_ids: List[str]
    anomaly_score: float
    risk_level: RiskLevel
    pattern_type: PatternType
    explanation: str
    recommended_action: str
    is_reviewed: bool = False
    is_true_positive: Optional[bool] = None
    reviewer_notes: Optional[str] = None


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    precision: float
    recall: float
    f1_score: float
    auc_roc: Optional[float] = None
    accuracy: Optional[float] = None
    confusion_matrix: Optional[List[List[int]]] = None


@dataclass
class DetectionResult:
    """Detection result"""
    anomaly_scores: List[float]
    risk_flags: List[RiskLevel]
    alerts: List[Alert]
    model_metrics: Optional[ModelMetrics] = None


class BaseDataImporter(ABC):
    """
    Abstract base class for data importers
    """
    
    @abstractmethod
    def import_data(self, file_path: str) -> Any:
        """
        Import data from file
        
        Args:
            file_path: Path to data file
            
        Returns:
            Imported data
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Any) -> ValidationResult:
        """
        Validate imported data
        
        Args:
            data: Data to validate
            
        Returns:
            ValidationResult
        """
        pass


class BaseFeatureExtractor(ABC):
    """
    Abstract base class for feature extractors
    """
    
    @abstractmethod
    def extract_features(self, trades: Any) -> Any:
        """
        Extract features from trade data
        
        Args:
            trades: Trade data
            
        Returns:
            Feature vectors
        """
        pass
    
    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names
        
        Returns:
            List of feature names
        """
        pass


class BaseModel(ABC):
    """
    Abstract base class for ML models
    """
    
    @abstractmethod
    def train(self, X_train: Any, y_train: Optional[Any] = None) -> None:
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels (optional for unsupervised)
        """
        pass
    
    @abstractmethod
    def predict(self, X: Any) -> Any:
        """
        Make predictions
        
        Args:
            X: Input features
            
        Returns:
            Predictions
        """
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """
        Save model to file
        
        Args:
            path: Output file path
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """
        Load model from file
        
        Args:
            path: Input file path
        """
        pass


class BaseDetector(ABC):
    """
    Abstract base class for pattern detectors
    """
    
    @abstractmethod
    def detect(self, trades: Any) -> List[Alert]:
        """
        Detect patterns in trade data
        
        Args:
            trades: Trade data
            
        Returns:
            List of alerts
        """
        pass
    
    @abstractmethod
    def get_pattern_type(self) -> PatternType:
        """
        Get pattern type this detector identifies
        
        Returns:
            PatternType
        """
        pass


class BaseReportGenerator(ABC):
    """
    Abstract base class for report generators
    """
    
    @abstractmethod
    def generate_report(self, data: Any) -> Any:
        """
        Generate report from data
        
        Args:
            data: Input data
            
        Returns:
            Generated report
        """
        pass
    
    @abstractmethod
    def export(self, report: Any, output_path: str, format: str) -> None:
        """
        Export report to file
        
        Args:
            report: Report to export
            output_path: Output file path
            format: Export format (pdf, csv, json)
        """
        pass


class BaseStorage(ABC):
    """
    Abstract base class for data storage
    """
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    def save_trades(self, trades: List[Trade]) -> bool:
        """
        Save trades to storage
        
        Args:
            trades: List of trades
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    def get_trades(self, filters: Optional[Dict[str, Any]] = None) -> List[Trade]:
        """
        Retrieve trades from storage
        
        Args:
            filters: Optional filters
            
        Returns:
            List of trades
        """
        pass
    
    @abstractmethod
    def save_alert(self, alert: Alert) -> bool:
        """
        Save alert to storage
        
        Args:
            alert: Alert to save
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    def get_alerts(self, filters: Optional[Dict[str, Any]] = None) -> List[Alert]:
        """
        Retrieve alerts from storage
        
        Args:
            filters: Optional filters
            
        Returns:
            List of alerts
        """
        pass


class Singleton:
    """
    Singleton metaclass for ensuring single instance
    """
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
