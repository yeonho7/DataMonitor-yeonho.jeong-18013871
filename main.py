from __future__ import annotations
import os
import subprocess
import sys

import config
from config import DATA_SAMPLES, DATA_ORDERS, DATA_DIR
from repository.sample_repository import SampleRepository
from repository.order_repository import OrderRepository
from controller.monitor_controller import MonitorController
from view.monitor_view import MonitorView


def main() -> None:
    sample_repo = SampleRepository(DATA_SAMPLES)
    order_repo = OrderRepository(DATA_ORDERS)
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
            subprocess.run(
                [sys.executable, "DummyDataGenerator/main.py"],
                env={**os.environ, "DATA_DIR": DATA_DIR},
            )
        elif choice == "0":
            view.display_message("종료합니다.")
            break
        else:
            view.display_message("올바른 메뉴를 선택하세요. (0/1/2/9)")


if __name__ == "__main__":
    main()
