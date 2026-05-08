from __future__ import annotations

_W = 62  # 전체 출력 폭 (ASCII 기준)


class MonitorView:
    def display_main_menu(self, summary: dict) -> None:
        print("\n" + "=" * _W)
        print("     DataMonitor  반도체 시료 생산주문관리 모니터링 도구")
        print("=" * _W)
        print(
            f"  등록 시료 {summary['sample_count']:>3}종   "
            f"총 재고 {summary['total_stock']:>6,} ea   "
            f"전체 주문 {summary['total_orders']:>3}건"
        )
        print("-" * _W)
        print("  [1] 주문량 확인")
        print("  [2] 재고량 확인")
        print("  [9] 더미 데이터 생성")
        print("  [0] 종료")
        print("-" * _W)

    def display_order_summary(self, order_summary: dict) -> None:
        self._section("주문 현황")
        total = 0
        for status, orders in order_summary.items():
            total += len(orders)
            print(f"  {status:<12}: {len(orders)}건")
            for o in orders:
                print(f"    · {o.order_id}  고객: {o.customer:<18}  수량: {o.quantity:>5} ea")
        print(f"  {'합계':<12}: {total}건")
        self._rule()

    def display_stock_status(self, stock_items: list[dict]) -> None:
        self._section("재고 현황")
        print(f"  {'시료명':<22} {'재고':>7} {'활성주문':>8} {'상태':>6} {'잔여율':>7}")
        self._rule()
        for item in stock_items:
            s = item["sample"]
            print(
                f"  {s.name:<22} {s.stock:>5} ea {item['active_order_qty']:>6} ea"
                f"  [{item['stock_status']}]  {item['remaining_pct']:>5.1f}%"
            )
        self._rule()

    def get_menu_input(self, prompt: str = "선택 > ") -> str:
        return input(prompt).strip()

    def display_message(self, message: str) -> None:
        print(f"  {message}")

    def _section(self, title: str) -> None:
        # 한글은 터미널 폭 2칸 → 뒤 대시는 고정 길이 사용
        print(f"\n  ── {title} " + "─" * 42)

    def _rule(self) -> None:
        print("  " + "─" * 58)
