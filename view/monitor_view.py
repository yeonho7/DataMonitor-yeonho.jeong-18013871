from __future__ import annotations


class MonitorView:
    def display_main_menu(self, summary: dict) -> None:
        print("\n" + "=" * 62)
        print("     DataMonitor  반도체 시료 생산주문관리 모니터링 도구")
        print("=" * 62)
        print(
            f"  등록 시료 {summary['sample_count']:>3}종   "
            f"총 재고 {summary['total_stock']:>6,} ea   "
            f"전체 주문 {summary['total_orders']:>3}건"
        )
        print("-" * 62)
        print("  [1] 주문량 확인")
        print("  [2] 재고량 확인")
        print("  [9] 더미 데이터 생성")
        print("  [0] 종료")
        print("-" * 62)

    def display_order_summary(self, order_summary: dict) -> None:
        print("\n  ── 주문 현황 ──────────────────────────────────────────")
        total = 0
        for status_name, orders in order_summary.items():
            count = len(orders)
            total += count
            print(f"  {status_name:<12}: {count}건")
            for o in orders:
                print(
                    f"    · {o.order_id}  고객: {o.customer:<18}  수량: {o.quantity:>5} ea"
                )
        print(f"  {'합계':<12}: {total}건")
        print("  " + "─" * 58)

    def display_stock_status(self, stock_items: list[dict]) -> None:
        print("\n  ── 재고 현황 ──────────────────────────────────────────")
        print(f"  {'시료명':<22} {'재고':>7} {'활성주문':>8} {'상태':>6} {'잔여율':>7}")
        print("  " + "─" * 58)
        for item in stock_items:
            s = item["sample"]
            label = f"[{item['stock_status']}]"
            print(
                f"  {s.name:<22} {s.stock:>5} ea {item['active_order_qty']:>6} ea"
                f" {label:>7} {item['remaining_pct']:>6.1f}%"
            )
        print("  " + "─" * 58)

    def get_menu_input(self, prompt: str = "선택 > ") -> str:
        return input(prompt).strip()

    def display_message(self, message: str) -> None:
        print(f"  {message}")
