from __future__ import annotations
import os
import sys

# stubs/를 맨 앞에 추가 — DataPersistence 서브모듈 대체
_STUBS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stubs")
if _STUBS not in sys.path:
    sys.path.insert(0, _STUBS)

from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.monitor_controller import MonitorController
from view.monitor_view import MonitorView

_BASE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_BASE, "data")
_DATA_SAMPLES = os.path.join(_DATA_DIR, "samples.json")
_DATA_ORDERS = os.path.join(_DATA_DIR, "orders.json")


def main() -> None:
    sample_repo = SampleRepository(_DATA_SAMPLES)
    order_repo = OrderRepository(_DATA_ORDERS)
    controller = MonitorController(sample_repo, order_repo)
    view = MonitorView()

    while True:
        summary = controller.get_summary()
        view.display_main_menu(summary)
        choice = view.get_menu_input()

        if choice == "1":
            view.display_order_summary(controller.get_order_status_summary())
        elif choice == "2":
            view.display_stock_status(controller.get_stock_status())
        elif choice == "9":
            view.display_message("[9] 더미 데이터 생성은 서브모듈(DummyDataGenerator)이 필요합니다.")
        elif choice == "0":
            view.display_message("종료합니다.")
            break
        else:
            view.display_message("올바른 메뉴를 선택하세요. (0/1/2/9)")


if __name__ == "__main__":
    main()
