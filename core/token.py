from abc import ABC, abstractmethod
from typing import Any

class TokenManager(ABC):
    @abstractmethod
    def get_balance(self, user_id: str) -> float:
        """Gets the token balance for a user."""
        pass

    @abstractmethod
    def transfer_tokens(self, from_user_id: str, to_user_id: str, amount: float) -> bool:
        """Transfers tokens between users."""
        pass

    @abstractmethod
    def record_transaction(self, transaction_details: Any) -> bool:
        """Records a transaction."""
        pass

from typing import List, Dict, Any
import datetime

class UserAccount:
    def __init__(self, user_id: str, initial_balance: float = 0.0):
        self.user_id: str = user_id
        self.balance: float = initial_balance
        self.transaction_history: List[Dict[str, Any]] = []
        self.access_rights: List[str] = ["basic_user"] # Example access rights

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self.balance += amount
        self._add_transaction(type="deposit", amount=amount)
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        self._add_transaction(type="withdrawal", amount=amount)
        return True

    def _add_transaction(self, type: str, amount: float, to_user: str = None, from_user: str = None):
        transaction = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "type": type,
            "amount": amount,
        }
        if to_user:
            transaction["to_user"] = to_user
        if from_user:
            transaction["from_user"] = from_user
        self.transaction_history.append(transaction)

    def __repr__(self):
        return f"UserAccount(user_id='{self.user_id}', balance={self.balance:.2f})"
