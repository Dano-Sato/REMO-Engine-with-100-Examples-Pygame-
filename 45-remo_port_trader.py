from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

import pygame

from REMOLib import *


TAGS = ["FOOD", "MED", "ORE", "PARTS", "DATA", "LUX"]


@dataclass(frozen=True)
class CargoCardData:
    name: str
    tag: str
    buy_cost: int
    base_sell: int
    sell_effect: str = ""


@dataclass(frozen=True)
class ActionCardData:
    name: str
    card_type: str
    cost: int
    description: str
    effect_key: str


@dataclass
class ContractCardData:
    name: str
    cost: int
    description: str
    reward: str
    effect_key: str


@dataclass(frozen=True)
class PortData:
    name: str
    bonus_tags: dict[str, int]
    penalty_tag: str
    service_desc: str


@dataclass
class MarketSlot:
    card: CargoCardData | ActionCardData | None = None
    reserved: bool = False


class CardTile(rectObj):
    def __init__(self, rect: pygame.Rect, title: str, subtitle: str, body: str, color: tuple[int, int, int]):
        super().__init__(rect, color=color, edge=4, radius=16)
        self._base_color = color
        self._hover_color = Cs.light(color)
        self._clickable = True
        self.title_text = textObj(title, size=20, color=Cs.white)
        self.title_text.setParent(self, depth=1)
        self.title_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 10)

        self.subtitle_text = textObj(subtitle, size=18, color=Cs.light(Cs.whitesmoke))
        self.subtitle_text.setParent(self, depth=1)
        self.subtitle_text.midtop = RPoint(self.offsetRect.midtop) + RPoint(0, 36)

        self.body_text = longTextObj(body, pos=RPoint(0, 0), size=18, color=Cs.white, textWidth=rect.width - 24)
        self.body_text.setParent(self, depth=1)
        self.body_text.centerx = self.offsetRect.centerx
        self.body_text.y = self.subtitle_text.rect.bottom + 6

    def set_content(self, title: str, subtitle: str, body: str) -> None:
        self.title_text.text = title
        self.subtitle_text.text = subtitle
        self.body_text.text = body

    def set_clickable(self, clickable: bool) -> None:
        self._clickable = clickable
        alpha = 255 if clickable else 150
        self.alpha = alpha
        self.title_text.alpha = alpha
        self.subtitle_text.alpha = alpha
        self.body_text.alpha = alpha

    def update(self) -> None:
        hovered = self.collideMouse()
        target = self._hover_color if hovered and self._clickable else self._base_color
        if self.color != target:
            self.color = target


class PortTraderScene(Scene):
    SCREEN_SIZE = (1920, 1080)
    HAND_LIMIT = 5
    BASE_ACTIONS = 1
    BASE_SELLS = 2
    BASE_BUYS = 1
    BASE_CARGO_LIMIT = 6

    def initOnce(self) -> None:
        self.random = random.Random()
        self._setup_data()
        self._setup_state()
        self._build_static_ui()
        self.refresh_all()

    def _setup_data(self) -> None:
        self.cargo_library = [
            CargoCardData("Ration Packs", "FOOD", 4, 6),
            CargoCardData("Hydroponic Greens", "FOOD", 6, 8),
            CargoCardData("Spice Crates", "FOOD", 7, 9, sell_effect="intel+1"),
            CargoCardData("Luxury Meal Kits", "FOOD", 9, 12, sell_effect="credits+2"),
            CargoCardData("First-Aid Pallets", "MED", 5, 7),
            CargoCardData("Antibiotic Crate", "MED", 7, 10),
            CargoCardData("Cryo Vials", "MED", 8, 11, sell_effect="parts+1"),
            CargoCardData("Surgical Suite Pod", "MED", 10, 14, sell_effect="sell+1"),
            CargoCardData("Raw Ore Sacks", "ORE", 4, 6),
            CargoCardData("Refined Ingots", "ORE", 6, 9),
            CargoCardData("Rare Mineral Chunks", "ORE", 8, 12),
            CargoCardData("Exotic Crystal Cache", "ORE", 10, 15, sell_effect="credits+3;next_fuel_zero"),
            CargoCardData("Spare Actuators", "PARTS", 5, 7),
            CargoCardData("Circuit Bundles", "PARTS", 6, 9, sell_effect="intel+1"),
            CargoCardData("Servo Assemblies", "PARTS", 8, 11),
            CargoCardData("Ship-Grade Components", "PARTS", 10, 14, sell_effect="action_discount_1"),
            CargoCardData("Survey Logs", "DATA", 5, 7),
            CargoCardData("Encrypted Archives", "DATA", 7, 10),
            CargoCardData("Blackbox Telemetry", "DATA", 8, 11, sell_effect="fuel+1"),
            CargoCardData("Quantum Dataset", "DATA", 10, 15, sell_effect="draw+1"),
            CargoCardData("Designer Spirits", "LUX", 6, 9),
            CargoCardData("Art Capsule", "LUX", 8, 12),
            CargoCardData("Celebrity Memorabilia", "LUX", 9, 13, sell_effect="credits+2"),
            CargoCardData("Couture Vault", "LUX", 11, 17, sell_effect="buy+1"),
        ]

        self.action_library = [
            ActionCardData("Deckhand", "Crew", 2, "Fuel +1", "deckhand"),
            ActionCardData("Quartermaster", "Crew", 4, "Draw +1, Parts +1", "quartermaster"),
            ActionCardData("Navigator", "Crew", 5, "Draw +2", "navigator"),
            ActionCardData("Accountant", "Crew", 4, "Intel +1, first buy -1", "accountant"),
            ActionCardData("Mechanic", "Crew", 4, "Parts +2", "mechanic"),
            ActionCardData("Route Planner", "Crew", 5, "Fuel +2, Buy +1", "route_planner"),
            ActionCardData("Efficient Shift", "Ops", 3, "Actions +2", "efficient_shift"),
            ActionCardData("Overtime Crew", "Ops", 3, "Actions +1, Draw +1", "overtime"),
            ActionCardData("Scrap Sorting", "Ops", 3, "Trash 1, Parts +1", "scrap_sorting"),
            ActionCardData("System Purge", "Ops", 5, "Trash 2", "system_purge"),
            ActionCardData("Deep Focus", "Ops", 4, "Intel +2, Draw +1", "deep_focus"),
            ActionCardData("Lucky Find", "Ops", 2, "Draw +1 (next turn draw -1)", "lucky_find"),
            ActionCardData("Market Scan", "Ops", 4, "Pay Intel1: buy cargo now", "market_scan"),
            ActionCardData("Price Negotiation", "Ops", 4, "First buy -2", "price_negotiation"),
            ActionCardData("Bulk Supplier", "Ops", 5, "Cargo buys -1 (2)", "bulk_supplier"),
            ActionCardData("Re-Listing", "Ops", 3, "Pay Fuel1: refresh cargo", "re_listing"),
            ActionCardData("Ad Campaign", "Ops", 4, "Choose tag: sell +2", "ad_campaign"),
            ActionCardData("Insider Tip", "Ops", 5, "Pay Intel2: ignore penalty", "insider_tip"),
            ActionCardData("Broker Network", "Ops", 6, "Sell +1, Buy +1", "broker_network"),
            ActionCardData("Hold Reservation", "Ops", 3, "Reserve market card", "hold_reservation"),
            ActionCardData("Clearance Sale", "Ops", 3, "Action buys -1 (2)", "clearance_sale"),
            ActionCardData("Port Gossip", "Ops", 2, "Intel +1, refresh cargo", "port_gossip"),
            ActionCardData("Cargo Netting", "Module", 4, "Cargo limit +1", "cargo_netting"),
            ActionCardData("Reinforced Racks", "Module", 6, "Cargo limit +2", "reinforced_racks"),
            ActionCardData("Quick Unload", "Ops", 3, "Sell +1", "quick_unload"),
            ActionCardData("Auctioneer", "Crew", 5, "Sales +1Cr (max 2)", "auctioneer"),
            ActionCardData("Cold Storage", "Module", 5, "FOOD/MED sell +1", "cold_storage"),
            ActionCardData("Cargo Swap", "Ops", 3, "Trash cargo, buy market -1", "cargo_swap"),
            ActionCardData("Manifest Optimization", "Ops", 4, "Sell 2+ same tag +3Cr", "manifest_opt"),
            ActionCardData("Dock Runner", "Crew", 4, "Fuel +1, Sell/Buy +1", "dock_runner"),
            ActionCardData("Contract Clerk", "Crew", 4, "Contract slots +1", "contract_clerk"),
            ActionCardData("Favored Client", "Module", 6, "Preferred bonus +1", "favored_client"),
            ActionCardData("Local Connections", "Ops", 5, "Cargo market +1", "local_connections"),
            ActionCardData("Warehouse Lease", "Module", 7, "Cargo limit +1, port start Parts +1", "warehouse_lease"),
            ActionCardData("Sales Pitch", "Ops", 3, "Advance contract +1", "sales_pitch"),
            ActionCardData("Priority Docking", "Ops", 5, "Action+1, Buy+1 (next turn action -1)", "priority_docking"),
        ]

        self.contract_library = [
            ContractCardData("Emergency Rations", 3, "Sell 2 FOOD", "+8Cr", "food_2"),
            ContractCardData("Clinic Restock", 4, "Sell 2 MED", "+10Cr", "med_2"),
            ContractCardData("Mineral Shipment", 3, "Sell 2 ORE", "+9Cr", "ore_2"),
            ContractCardData("Shipyard Order", 4, "Sell 2 PARTS", "+10Cr", "parts_2"),
            ContractCardData("Data Licensing", 4, "Sell 2 DATA", "+11Cr", "data_2"),
            ContractCardData("Luxury Showcase", 5, "Sell 2 LUX", "+14Cr", "lux_2"),
            ContractCardData("Mixed Manifest", 4, "Sell 3 different tags", "+12Cr", "mixed_3"),
            ContractCardData("Bulk Deal", 5, "Sell 3 same tag", "+15Cr", "bulk_3"),
            ContractCardData("Fast Turnaround", 3, "Sell 2 in one turn", "+7Cr + Fuel1", "fast_turn"),
            ContractCardData("Premium Bundle", 5, "Sell LUX + DATA", "+16Cr", "lux_data"),
            ContractCardData("Shipwright’s Special", 4, "Sell PARTS + ORE", "+12Cr + Parts next", "parts_ore"),
            ContractCardData("Field Hospital", 4, "Sell MED + FOOD", "+11Cr + Intel next", "med_food"),
            ContractCardData("Prospector’s Cache", 5, "Sell ORE + DATA", "+14Cr + refresh", "ore_data"),
            ContractCardData("High Society", 5, "Sell LUX + MED", "+15Cr + Sell+1", "lux_med"),
            ContractCardData("Port Reputation", 4, "Sell 2 preferred tags", "+9Cr + pref+1", "port_rep"),
            ContractCardData("Clear the Shelves", 3, "Sell 1 nonpreferred", "+8Cr", "nonpref"),
            ContractCardData("Market Maker", 4, "Buy & sell same turn", "+10Cr", "market_maker"),
            ContractCardData("Supplier Loop", 5, "3 turns with sale", "+18Cr", "supplier_loop"),
            ContractCardData("Expansion Funding", 6, "Sell 5 total in port", "Cargo limit +1", "expansion"),
            ContractCardData("Broker’s Bonus", 6, "Complete 2 contracts", "+20Cr", "broker_bonus"),
        ]

        self.ports = [
            PortData("Mining Colony", {"ORE": 5, "PARTS": 3}, "LUX", "Pay Parts1: refresh cargo"),
            PortData("Festival World", {"LUX": 6, "FOOD": 2}, "ORE", "Pay Fuel1: Sell +1"),
            PortData("Medical Hub", {"MED": 5, "DATA": 2}, "FOOD", "Pay Intel1: first sale +3Cr"),
            PortData("Data Exchange", {"DATA": 6, "LUX": 1}, "ORE", "Pay Intel2: refresh action"),
            PortData("Industrial Shipyard", {"PARTS": 5, "ORE": 2}, "MED", "First action buy -2Cr"),
            PortData("Agri Ring", {"FOOD": 5, "MED": 1}, "DATA", "Pay Parts1: cargo limit +1"),
            PortData("Luxury Spindle", {"LUX": 5, "MED": 2}, "PARTS", "Pay 2Cr: buy cargo free slot"),
            PortData("Frontier Bazaar", {"FOOD": 3, "ORE": 3}, "LUX", "Pay Fuel1: Buy +1"),
        ]

    def _setup_state(self) -> None:
        self.credits = 12
        self.fuel = 0
        self.parts = 0
        self.intel = 0
        self.turn = 1
        self.port_turn = 1
        self.port_index = 0
        self.phase = "Operate"
        self.actions_left = self.BASE_ACTIONS
        self.sells_left = self.BASE_SELLS
        self.buys_left = self.BASE_BUYS
        self.cargo_limit = self.BASE_CARGO_LIMIT
        self.contract_slots = 2
        self.market_cargo_slots = 3
        self.market_action_slots = 3
        self.cargo_bay: list[CargoCardData] = []
        self.action_discard: list[ActionCardData] = []
        self.action_draw: list[ActionCardData] = []
        self.action_hand: list[ActionCardData] = []
        self.active_contracts: list[ContractCardData] = []
        self.completed_contracts: list[str] = []
        self.contract_progress: dict[str, dict[str, int] | set[str] | int | bool] = {}
        self.contract_turn_tracker: dict[str, set[int]] = {}
        self.pending_message = ""
        self.log_lines: list[str] = []
        self.permanent_sell_bonus: dict[str, int] = {}
        self.modules_installed: set[str] = set()
        self._reset_turn_flags()
        self._build_decks()
        self._draw_cards(self.HAND_LIMIT)
        self._setup_market()
        self._setup_contract_offers()
        self.port_bonus_adjust: dict[str, int] = {}
        self.next_turn_draw_bonus = 0
        self.next_turn_draw_penalty = 0
        self.next_turn_fuel_bonus = 0
        self.next_turn_parts_bonus = 0
        self.next_turn_intel_bonus = 0
        self.next_turn_actions_bonus = 0
        self.next_turn_buy_bonus = 0
        self.bought_this_turn: list[CargoCardData] = []
        self.manifest_opt_active = False
        self.manifest_opt_triggered = False
        self.port_favored_applied = False

    def _reset_turn_flags(self) -> None:
        self.action_cost_discount = 0
        self.action_cost_discount_uses = 0
        self.buy_discount = 0
        self.buy_discount_uses = 0
        self.cargo_buy_discount = 0
        self.cargo_buy_discount_uses = 0
        self.sell_bonus_tag: str | None = None
        self.sell_bonus_value = 0
        self.sell_bonus_flat = 0
        self.sell_bonus_first = 0
        self.sell_bonus_per_sale = 0
        self.sell_bonus_per_sale_uses = 0
        self.ignore_penalty = False
        self.market_scan_active = False
        self.cargo_swap_active = False
        self.reserved_slots: set[tuple[str, int]] = set()
        self.turn_sales_count = 0
        self.turn_sales_tags: list[str] = []
        self.turn_sales_same_turn_bought = False
        self.bought_this_turn = []
        self.manifest_opt_active = False
        self.manifest_opt_triggered = False
        self.first_sale_done = False

    def _build_decks(self) -> None:
        self.cargo_deck = self.cargo_library[:]
        self.random.shuffle(self.cargo_deck)
        self.action_market_deck = self.action_library[:]
        self.random.shuffle(self.action_market_deck)
        starter = [self._action_by_name("Deckhand")] * 3 + [self._action_by_name("Mechanic")] * 2
        starter += [self._action_by_name("Accountant")] * 2 + [self._action_by_name("Navigator")]
        self.action_draw = starter[:]
        self.random.shuffle(self.action_draw)

    def _action_by_name(self, name: str) -> ActionCardData:
        return next(card for card in self.action_library if card.name == name)

    def _cargo_by_name(self, name: str) -> CargoCardData:
        return next(card for card in self.cargo_library if card.name == name)

    def _setup_market(self) -> None:
        self.market_cargo = [MarketSlot() for _ in range(self.market_cargo_slots)]
        self.market_action = [MarketSlot() for _ in range(self.market_action_slots)]
        self._refill_market(initial=True)

    def _setup_contract_offers(self) -> None:
        self.contract_deck = self.contract_library[:]
        self.random.shuffle(self.contract_deck)
        self.contract_offers: list[ContractCardData | None] = [None, None]
        self._refill_contract_offers()

    def _refill_contract_offers(self) -> None:
        for idx in range(len(self.contract_offers)):
            if self.contract_offers[idx] is None and self.contract_deck:
                self.contract_offers[idx] = self.contract_deck.pop()

    def _draw_cards(self, count: int) -> None:
        for _ in range(count):
            if not self.action_draw:
                if not self.action_discard:
                    break
                self.action_draw = self.action_discard[:]
                self.action_discard.clear()
                self.random.shuffle(self.action_draw)
            self.action_hand.append(self.action_draw.pop())

    def _refill_market(self, initial: bool = False) -> None:
        for idx, slot in enumerate(self.market_cargo):
            if slot.card is None and not slot.reserved:
                if not self.cargo_deck:
                    self.cargo_deck = self.cargo_library[:]
                    self.random.shuffle(self.cargo_deck)
                slot.card = self.cargo_deck.pop()
                if not initial:
                    self._log(f"시장에 화물 입고: {slot.card.name}")

        for idx, slot in enumerate(self.market_action):
            if slot.card is None and not slot.reserved:
                if not self.action_market_deck:
                    self.action_market_deck = self.action_library[:]
                    self.random.shuffle(self.action_market_deck)
                slot.card = self.action_market_deck.pop()

    def _build_static_ui(self) -> None:
        self.title = textObj("REMO Port Trader", size=40, color=Cs.white)
        self.title.midtop = Rs.screenRect().midtop + RPoint(0, 10)

        self.phase_text = textObj("", size=28, color=Cs.yellow)
        self.phase_text.midtop = Rs.screenRect().midtop + RPoint(0, 60)

        self.status_text = longTextObj("", pos=RPoint(30, 110), size=20, color=Cs.white, textWidth=520)
        self.log_text = longTextObj("", pos=RPoint(30, 380), size=18, color=Cs.light(Cs.whitesmoke), textWidth=520)

        self.next_phase_button = rectObj(pygame.Rect(30, 920, 220, 60), color=Cs.dark(Cs.steelblue), edge=4)
        self.next_phase_label = textObj("Next Phase", size=22, color=Cs.white)
        self.next_phase_label.setParent(self.next_phase_button, depth=1)
        self.next_phase_label.center = self.next_phase_button.offsetRect.center

        self.end_turn_button = rectObj(pygame.Rect(270, 920, 220, 60), color=Cs.dark(Cs.sienna), edge=4)
        self.end_turn_label = textObj("End Turn", size=22, color=Cs.white)
        self.end_turn_label.setParent(self.end_turn_button, depth=1)
        self.end_turn_label.center = self.end_turn_button.offsetRect.center

        self.service_button = rectObj(pygame.Rect(30, 860, 460, 50), color=Cs.dark(Cs.darkslateblue), edge=4)
        self.service_label = textObj("Port Service", size=20, color=Cs.white)
        self.service_label.setParent(self.service_button, depth=1)
        self.service_label.center = self.service_button.offsetRect.center

        self.market_title = textObj("Market (Cargo 3 / Action 3)", size=26, color=Cs.white)
        self.market_title.topleft = RPoint(600, 100)
        self.cargo_title = textObj("Cargo Market", size=22, color=Cs.light(Cs.white))
        self.cargo_title.topleft = RPoint(600, 140)
        self.action_title = textObj("Action Market", size=22, color=Cs.light(Cs.white))
        self.action_title.topleft = RPoint(600, 420)

        self.cargo_tiles: list[CardTile] = []
        self.action_tiles: list[CardTile] = []
        self.contract_tiles: list[CardTile] = []
        self.hand_tiles: list[CardTile] = []
        self.cargo_bay_tiles: list[CardTile] = []

    def refresh_all(self) -> None:
        port = self.current_port()
        preferred = ", ".join(port.bonus_tags.keys())
        penalty = port.penalty_tag
        self.phase_text.text = f"Turn {self.turn} / Port Turn {self.port_turn} - {self.phase}"
        status_lines = [
            f"Port: {port.name} (Preferred: {preferred} / Penalty: {penalty})",
            f"Credits: {self.credits}Cr",
            f"Fuel {self.fuel} | Parts {self.parts} | Intel {self.intel}",
            f"Actions {self.actions_left} | Sells {self.sells_left} | Buys {self.buys_left}",
            f"Cargo Bay: {len(self.cargo_bay)}/{self.cargo_limit}",
            f"Contracts: {len(self.active_contracts)}/{self.contract_slots}",
        ]
        self.status_text.text = "\n".join(status_lines)
        self.log_text.text = "\n".join(self.log_lines[-8:])
        self.market_title.text = f"Market (Cargo {self.market_cargo_slots} / Action {self.market_action_slots})"
        self.service_label.text = f"Port Service: {port.service_desc}"
        self._refresh_market_tiles()
        self._refresh_hand_tiles()
        self._refresh_cargo_bay_tiles()
        self._refresh_contract_tiles()

    def _refresh_market_tiles(self) -> None:
        self.cargo_tiles.clear()
        for idx, slot in enumerate(self.market_cargo):
            rect = pygame.Rect(600 + idx * 240, 180, 220, 210)
            title = "Empty"
            subtitle = ""
            body = "다음 턴 시작에 채워짐"
            if slot.card:
                card = slot.card
                title = card.name
                subtitle = f"{card.tag} | Buy {card.buy_cost} / Sell {card.base_sell}"
                body = card.sell_effect or "No special"
            tile = CardTile(rect, title, subtitle, body, Cs.dark(Cs.teal))
            tile.set_clickable(slot.card is not None)
            self.cargo_tiles.append(tile)

        self.action_tiles.clear()
        for idx, slot in enumerate(self.market_action):
            rect = pygame.Rect(600 + idx * 240, 460, 220, 210)
            title = "Empty"
            subtitle = ""
            body = "다음 턴 시작에 채워짐"
            if slot.card:
                card = slot.card
                title = card.name
                subtitle = f"{card.card_type} | Cost {card.cost}"
                body = card.description
            tile = CardTile(rect, title, subtitle, body, Cs.dark(Cs.indigo))
            tile.set_clickable(slot.card is not None)
            self.action_tiles.append(tile)

    def _refresh_hand_tiles(self) -> None:
        self.hand_tiles.clear()
        for idx, card in enumerate(self.action_hand):
            rect = pygame.Rect(600 + idx * 190, 760, 175, 190)
            tile = CardTile(rect, card.name, f"{card.card_type} | Cost {card.cost}", card.description, Cs.dark(Cs.darkslategray))
            tile.set_clickable(self.phase == "Operate" and self.actions_left > 0)
            self.hand_tiles.append(tile)

    def _refresh_cargo_bay_tiles(self) -> None:
        self.cargo_bay_tiles.clear()
        for idx, card in enumerate(self.cargo_bay):
            rect = pygame.Rect(600 + idx * 150, 700, 140, 60)
            tile = CardTile(rect, card.name, card.tag, f"Sell {card.base_sell}", Cs.dark(Cs.darkolivegreen))
            tile.set_clickable(self.phase == "Sell" and self.sells_left > 0)
            self.cargo_bay_tiles.append(tile)

    def _refresh_contract_tiles(self) -> None:
        self.contract_tiles.clear()
        for idx, contract in enumerate(self.contract_offers):
            rect = pygame.Rect(1380 + idx * 220, 180, 200, 200)
            title = "No Offer"
            subtitle = ""
            body = "다음 항구에서 변경"
            if contract:
                title = contract.name
                subtitle = f"Cost {contract.cost}"
                body = f"{contract.description}\nReward: {contract.reward}"
            tile = CardTile(rect, title, subtitle, body, Cs.dark(Cs.sienna))
            tile.set_clickable(contract is not None)
            self.contract_tiles.append(tile)

    def current_port(self) -> PortData:
        return self.ports[self.port_index]

    def update(self) -> None:
        self._handle_buttons()
        self._handle_market_clicks()
        self._handle_hand_clicks()
        self._handle_cargo_clicks()
        self._handle_contract_clicks()
        self.refresh_all()
        for tile in self.cargo_tiles + self.action_tiles + self.hand_tiles + self.cargo_bay_tiles + self.contract_tiles:
            tile.update()

    def draw(self) -> None:
        self.title.draw()
        self.phase_text.draw()
        self.status_text.draw()
        self.log_text.draw()
        self.market_title.draw()
        self.cargo_title.draw()
        self.action_title.draw()
        self.next_phase_button.draw()
        self.end_turn_button.draw()
        self.service_button.draw()
        for tile in self.cargo_tiles + self.action_tiles + self.hand_tiles + self.cargo_bay_tiles + self.contract_tiles:
            tile.draw()

    def _handle_buttons(self) -> None:
        if self.next_phase_button.collideMouse() and Rs.userJustLeftClicked():
            self._advance_phase()
        if self.end_turn_button.collideMouse() and Rs.userJustLeftClicked():
            self._end_turn()
        if self.service_button.collideMouse() and Rs.userJustLeftClicked():
            self._use_port_service()

    def _handle_market_clicks(self) -> None:
        for idx, tile in enumerate(self.cargo_tiles):
            if tile.collideMouse() and Rs.userJustLeftClicked():
                self._buy_cargo(idx)
                return
        for idx, tile in enumerate(self.action_tiles):
            if tile.collideMouse() and Rs.userJustLeftClicked():
                self._buy_action(idx)
                return

    def _handle_hand_clicks(self) -> None:
        if self.phase != "Operate":
            return
        for idx, tile in enumerate(self.hand_tiles):
            if tile.collideMouse() and Rs.userJustLeftClicked():
                self._play_action(idx)
                return

    def _handle_cargo_clicks(self) -> None:
        if self.phase != "Sell":
            return
        for idx, tile in enumerate(self.cargo_bay_tiles):
            if tile.collideMouse() and Rs.userJustLeftClicked():
                self._sell_cargo(idx)
                return

    def _handle_contract_clicks(self) -> None:
        if self.phase != "Buy":
            return
        for idx, tile in enumerate(self.contract_tiles):
            if tile.collideMouse() and Rs.userJustLeftClicked():
                self._buy_contract(idx)
                return

    def _advance_phase(self) -> None:
        if self.phase == "Operate":
            self.phase = "Sell"
        elif self.phase == "Sell":
            self.phase = "Buy"
        else:
            self.phase = "Operate"
        self._log(f"페이즈 전환: {self.phase}")

    def _end_turn(self) -> None:
        self._apply_end_turn_contracts()
        self.port_turn += 1
        self.turn += 1
        if self.port_turn > 3:
            self.port_turn = 1
            self.port_index = (self.port_index + 1) % len(self.ports)
            self._on_new_port()
        self._start_turn()

    def _on_new_port(self) -> None:
        self._log("항구 이동! 새로운 항구 효과가 적용됩니다.")
        self.contract_offers = [None, None]
        self._refill_contract_offers()
        self._reset_port_contracts()
        self.market_cargo_slots = 3
        self.market_action_slots = 3
        if "local_connections" in self.modules_installed:
            self.market_cargo_slots += 1
        self._setup_market()

    def _start_turn(self) -> None:
        self.phase = "Operate"
        self.fuel = 0 + self.next_turn_fuel_bonus
        self.parts = 0 + self.next_turn_parts_bonus
        self.intel = 0 + self.next_turn_intel_bonus
        if "warehouse_lease" in self.modules_installed and self.port_turn == 1:
            self.parts += 1
        self.actions_left = self.BASE_ACTIONS + self.next_turn_actions_bonus
        self.buys_left = self.BASE_BUYS + self.next_turn_buy_bonus
        self.sells_left = self.BASE_SELLS
        draw_count = self.HAND_LIMIT + self.next_turn_draw_bonus - self.next_turn_draw_penalty
        self.next_turn_draw_bonus = 0
        self.next_turn_draw_penalty = 0
        self.next_turn_fuel_bonus = 0
        self.next_turn_parts_bonus = 0
        self.next_turn_intel_bonus = 0
        self.next_turn_actions_bonus = 0
        self.next_turn_buy_bonus = 0
        self._draw_cards(max(0, draw_count - len(self.action_hand)))
        self._refill_market()
        self._clear_reservations()
        self._log("턴 시작: 자원 리셋 및 시장 보충")
        self._reset_turn_flags()
        self._update_port_passives()

    def _update_port_passives(self) -> None:
        if "favored_client" in self.modules_installed and not self.port_favored_applied:
            for tag in self.current_port().bonus_tags:
                self.port_bonus_adjust[tag] = self.port_bonus_adjust.get(tag, 0) + 1
            self.port_favored_applied = True

    def _reset_port_contracts(self) -> None:
        self.active_contracts.clear()
        self.completed_contracts.clear()
        self.contract_progress.clear()
        self.contract_turn_tracker.clear()
        self.port_bonus_adjust.clear()
        self.port_favored_applied = False

    def _apply_end_turn_contracts(self) -> None:
        for contract in self.active_contracts[:]:
            if contract.effect_key == "supplier_loop":
                if self.turn_sales_count > 0:
                    turns = self.contract_turn_tracker.setdefault(contract.name, set())
                    turns.add(self.port_turn)
                    if len(turns) >= 3:
                        self._complete_contract(contract)
        self.turn_sales_count = 0
        self.turn_sales_tags.clear()
        self.turn_sales_same_turn_bought = False

    def _buy_cargo(self, index: int) -> None:
        if self.phase != "Buy" and not self.market_scan_active and not self.cargo_swap_active:
            self._log("구매는 Buy 페이즈에서만 가능합니다.")
            return
        if self.buys_left <= 0 and not (self.market_scan_active or self.cargo_swap_active):
            self._log("이번 턴 구매 횟수가 없습니다.")
            return
        if len(self.cargo_bay) >= self.cargo_limit:
            self._log("적재칸이 가득 찼습니다.")
            return
        slot = self.market_cargo[index]
        if not slot.card:
            return
        card = slot.card
        cost = card.buy_cost
        if self.cargo_swap_active:
            cost = max(0, cost - 1)
        if self.cargo_buy_discount_uses > 0:
            cost = max(0, cost - self.cargo_buy_discount)
            self.cargo_buy_discount_uses -= 1
        if self.buy_discount_uses > 0:
            cost = max(0, cost - self.buy_discount)
            self.buy_discount_uses -= 1
        if cost > self.credits:
            self._log("크레딧이 부족합니다.")
            return
        self.credits -= cost
        self.cargo_bay.append(card)
        self.bought_this_turn.append(card)
        slot.card = None
        slot.reserved = False
        if not self.market_scan_active and not self.cargo_swap_active:
            self.buys_left -= 1
        self.market_scan_active = False
        self.cargo_swap_active = False
        self._log(f"{card.name} 구매 (-{cost}Cr)")

    def _buy_action(self, index: int) -> None:
        if self.phase != "Buy":
            self._log("구매는 Buy 페이즈에서만 가능합니다.")
            return
        if self.buys_left <= 0:
            self._log("이번 턴 구매 횟수가 없습니다.")
            return
        slot = self.market_action[index]
        if not slot.card:
            return
        card = slot.card
        cost = card.cost
        if self.action_cost_discount_uses > 0:
            cost = max(0, cost - self.action_cost_discount)
            self.action_cost_discount_uses -= 1
        if cost > self.credits:
            self._log("크레딧이 부족합니다.")
            return
        self.credits -= cost
        self.action_discard.append(card)
        slot.card = None
        self.buys_left -= 1
        self._log(f"{card.name} 구매 (-{cost}Cr)")

    def _buy_contract(self, index: int) -> None:
        if self.phase != "Buy":
            return
        contract = self.contract_offers[index]
        if not contract:
            return
        if len(self.active_contracts) >= self.contract_slots:
            self._log("계약 슬롯이 가득 찼습니다.")
            return
        if contract.cost > self.credits:
            self._log("크레딧이 부족합니다.")
            return
        self.credits -= contract.cost
        self.active_contracts.append(contract)
        self.contract_offers[index] = None
        self._log(f"계약 체결: {contract.name}")
        self._initialize_contract_progress(contract)

    def _initialize_contract_progress(self, contract: ContractCardData) -> None:
        if contract.effect_key in {"food_2", "med_2", "ore_2", "parts_2", "data_2", "lux_2"}:
            self.contract_progress[contract.name] = 0
        elif contract.effect_key == "mixed_3":
            self.contract_progress[contract.name] = set()
        elif contract.effect_key == "bulk_3":
            self.contract_progress[contract.name] = {"max": 0, "counts": {}}
        elif contract.effect_key == "fast_turn":
            self.contract_progress[contract.name] = 0
        elif contract.effect_key in {"lux_data", "parts_ore", "med_food", "ore_data", "lux_med"}:
            self.contract_progress[contract.name] = set()
        elif contract.effect_key == "port_rep":
            self.contract_progress[contract.name] = 0
        elif contract.effect_key == "nonpref":
            self.contract_progress[contract.name] = 0
        elif contract.effect_key == "market_maker":
            self.contract_progress[contract.name] = False
        elif contract.effect_key == "supplier_loop":
            self.contract_turn_tracker[contract.name] = set()
        elif contract.effect_key == "expansion":
            self.contract_progress[contract.name] = 0
        elif contract.effect_key == "broker_bonus":
            self.contract_progress[contract.name] = 0

    def _play_action(self, index: int) -> None:
        if self.phase != "Operate" or self.actions_left <= 0:
            return
        card = self.action_hand.pop(index)
        self.actions_left -= 1
        self._resolve_action(card)
        if card.card_type == "Module":
            self._install_module(card.effect_key)
        else:
            self.action_discard.append(card)
        self._log(f"Action 사용: {card.name}")

    def _resolve_action(self, card: ActionCardData) -> None:
        effect = card.effect_key
        if effect == "deckhand":
            self.fuel += 1
        elif effect == "quartermaster":
            self.parts += 1
            self._draw_cards(1)
        elif effect == "navigator":
            self._draw_cards(2)
        elif effect == "accountant":
            self.intel += 1
            self.buy_discount = 1
            self.buy_discount_uses = max(self.buy_discount_uses, 1)
        elif effect == "mechanic":
            self.parts += 2
        elif effect == "route_planner":
            self.fuel += 2
            self.buys_left += 1
        elif effect == "efficient_shift":
            self.actions_left += 2
        elif effect == "overtime":
            self.actions_left += 1
            self._draw_cards(1)
        elif effect == "scrap_sorting":
            self.parts += 1
            self._trash_from_hand(1)
        elif effect == "system_purge":
            self._trash_from_hand(2)
        elif effect == "deep_focus":
            self.intel += 2
            self._draw_cards(1)
        elif effect == "lucky_find":
            self._draw_cards(1)
            self.next_turn_draw_penalty += 1
        elif effect == "market_scan":
            if self.intel >= 1:
                self.intel -= 1
                self.market_scan_active = True
                self._log("Market Scan: 다음 화물 구매는 Buy 소모 없음")
            else:
                self._log("Intel이 부족합니다.")
        elif effect == "price_negotiation":
            self.buy_discount = max(self.buy_discount, 2)
            self.buy_discount_uses = max(self.buy_discount_uses, 1)
        elif effect == "bulk_supplier":
            self.cargo_buy_discount = max(self.cargo_buy_discount, 1)
            self.cargo_buy_discount_uses = max(self.cargo_buy_discount_uses, 2)
        elif effect == "re_listing":
            if self.fuel >= 1:
                self.fuel -= 1
                self._refresh_market_slot(self.market_cargo)
            else:
                self._log("Fuel이 부족합니다.")
        elif effect == "ad_campaign":
            tag = self._select_best_tag()
            self.sell_bonus_tag = tag
            self.sell_bonus_value = 2
        elif effect == "insider_tip":
            if self.intel >= 2:
                self.intel -= 2
                self.ignore_penalty = True
            else:
                self._log("Intel이 부족합니다.")
        elif effect == "broker_network":
            self.sells_left += 1
            self.buys_left += 1
        elif effect == "hold_reservation":
            self._reserve_market_slot()
        elif effect == "clearance_sale":
            self.action_cost_discount = max(self.action_cost_discount, 1)
            self.action_cost_discount_uses = max(self.action_cost_discount_uses, 2)
        elif effect == "port_gossip":
            self.intel += 1
            self._refresh_market_slot(self.market_cargo)
        elif effect == "cargo_netting":
            self.cargo_limit += 1
            self.modules_installed.add(effect)
        elif effect == "reinforced_racks":
            self.cargo_limit += 2
            self.modules_installed.add(effect)
        elif effect == "quick_unload":
            self.sells_left += 1
        elif effect == "auctioneer":
            self.sell_bonus_per_sale = max(self.sell_bonus_per_sale, 1)
            self.sell_bonus_per_sale_uses = max(self.sell_bonus_per_sale_uses, 2)
        elif effect == "cold_storage":
            self.permanent_sell_bonus["FOOD"] = self.permanent_sell_bonus.get("FOOD", 0) + 1
            self.permanent_sell_bonus["MED"] = self.permanent_sell_bonus.get("MED", 0) + 1
            self.modules_installed.add(effect)
        elif effect == "cargo_swap":
            if self.cargo_bay:
                removed = self.cargo_bay.pop()
                self._log(f"Cargo Swap: {removed.name} 폐기")
                self.cargo_swap_active = True
            else:
                self._log("적재칸에 화물이 없습니다.")
        elif effect == "manifest_opt":
            self.manifest_opt_active = True
        elif effect == "dock_runner":
            self.fuel += 1
            if self.sells_left <= self.buys_left:
                self.sells_left += 1
            else:
                self.buys_left += 1
        elif effect == "contract_clerk":
            self.contract_slots += 1
            self.modules_installed.add(effect)
        elif effect == "favored_client":
            self.modules_installed.add(effect)
        elif effect == "local_connections":
            self.modules_installed.add(effect)
            self.market_cargo_slots = 4
            self._setup_market()
        elif effect == "warehouse_lease":
            self.modules_installed.add(effect)
            self.cargo_limit += 1
        elif effect == "sales_pitch":
            if self.active_contracts:
                self._boost_contract(self.active_contracts[0])
        elif effect == "priority_docking":
            self.actions_left += 1
            self.buys_left += 1
            self.next_turn_actions_bonus -= 1
        else:
            self._log(f"효과 미구현: {effect}")

    def _install_module(self, effect_key: str) -> None:
        if effect_key in {"cargo_netting", "reinforced_racks", "cold_storage", "contract_clerk", "favored_client", "warehouse_lease"}:
            return
        if effect_key == "local_connections":
            return

    def _trash_from_hand(self, count: int) -> None:
        for _ in range(min(count, len(self.action_hand))):
            removed = self.action_hand.pop(0)
            self._log(f"폐기: {removed.name}")

    def _refresh_market_slot(self, slots: list[MarketSlot]) -> None:
        for slot in slots:
            if slot.card is not None:
                if slots is self.market_cargo:
                    if not self.cargo_deck:
                        self.cargo_deck = self.cargo_library[:]
                        self.random.shuffle(self.cargo_deck)
                    slot.card = self.cargo_deck.pop()
                else:
                    if not self.action_market_deck:
                        self.action_market_deck = self.action_library[:]
                        self.random.shuffle(self.action_market_deck)
                    slot.card = self.action_market_deck.pop()
                break

    def _reserve_market_slot(self) -> None:
        for idx, slot in enumerate(self.market_cargo):
            if slot.card and ("cargo", idx) not in self.reserved_slots:
                slot.reserved = True
                self.reserved_slots.add(("cargo", idx))
                self._log(f"예약됨: {slot.card.name}")
                return

    def _sell_cargo(self, index: int) -> None:
        if self.phase != "Sell" or self.sells_left <= 0:
            return
        card = self.cargo_bay.pop(index)
        same_turn_bought = False
        if card in self.bought_this_turn:
            self.bought_this_turn.remove(card)
            same_turn_bought = True
            self.turn_sales_same_turn_bought = True
        sale = card.base_sell
        port = self.current_port()
        if card.tag in port.bonus_tags:
            sale += port.bonus_tags[card.tag] + self.port_bonus_adjust.get(card.tag, 0)
        elif card.tag == port.penalty_tag and not self.ignore_penalty:
            sale -= 2
        sale += self.permanent_sell_bonus.get(card.tag, 0)
        if self.sell_bonus_tag == card.tag:
            sale += self.sell_bonus_value
        if self.sell_bonus_first > 0 and not self.first_sale_done:
            sale += self.sell_bonus_first
        if self.sell_bonus_per_sale_uses > 0:
            sale += self.sell_bonus_per_sale
            self.sell_bonus_per_sale_uses -= 1
        sale = max(0, sale)
        self.credits += sale
        self.sells_left -= 1
        self.first_sale_done = True
        self.turn_sales_count += 1
        self.turn_sales_tags.append(card.tag)
        if card.sell_effect:
            self._resolve_cargo_sell_effect(card)
        self._advance_contracts_after_sale(card, same_turn_bought)
        if self.manifest_opt_active and not self.manifest_opt_triggered:
            if any(self.turn_sales_tags.count(tag) >= 2 for tag in set(self.turn_sales_tags)):
                self.credits += 3
                self.manifest_opt_triggered = True
        self._log(f"{card.name} 판매 +{sale}Cr")

    def _resolve_cargo_sell_effect(self, card: CargoCardData) -> None:
        effect = card.sell_effect
        if effect == "intel+1":
            self.intel += 1
        elif effect == "credits+2":
            self.credits += 2
        elif effect == "parts+1":
            self.parts += 1
        elif effect == "sell+1":
            self.sells_left += 1
        elif effect == "credits+3;next_fuel_zero":
            self.credits += 3
            self.next_turn_fuel_bonus += -self.fuel
        elif effect == "action_discount_1":
            self.action_cost_discount = max(self.action_cost_discount, 1)
            self.action_cost_discount_uses = max(self.action_cost_discount_uses, 1)
        elif effect == "fuel+1":
            self.fuel += 1
        elif effect == "draw+1":
            self._draw_cards(1)
        elif effect == "buy+1":
            self.buys_left += 1

    def _advance_contracts_after_sale(self, card: CargoCardData, same_turn: bool) -> None:
        for contract in self.active_contracts[:]:
            self._advance_contract_progress(contract, card.tag, same_turn=same_turn)

    def _advance_contract_progress(self, contract: ContractCardData, tag: str | None, same_turn: bool) -> None:
        key = contract.effect_key
        progress = self.contract_progress.get(contract.name)
        if key == "food_2" and tag == "FOOD":
            self.contract_progress[contract.name] += 1
        elif key == "med_2" and tag == "MED":
            self.contract_progress[contract.name] += 1
        elif key == "ore_2" and tag == "ORE":
            self.contract_progress[contract.name] += 1
        elif key == "parts_2" and tag == "PARTS":
            self.contract_progress[contract.name] += 1
        elif key == "data_2" and tag == "DATA":
            self.contract_progress[contract.name] += 1
        elif key == "lux_2" and tag == "LUX":
            self.contract_progress[contract.name] += 1
        elif key == "mixed_3":
            if tag:
                progress.add(tag)
        elif key == "bulk_3":
            if tag:
                counts = self.contract_progress.setdefault(contract.name, {"max": 0, "counts": {}})
                counts["counts"][tag] = counts["counts"].get(tag, 0) + 1
                counts["max"] = max(counts["max"], counts["counts"][tag])
        elif key == "fast_turn":
            if self.turn_sales_count >= 2:
                self.contract_progress[contract.name] = 2
        elif key == "lux_data":
            if tag in {"LUX", "DATA"}:
                progress.add(tag)
        elif key == "parts_ore":
            if tag in {"PARTS", "ORE"}:
                progress.add(tag)
        elif key == "med_food":
            if tag in {"MED", "FOOD"}:
                progress.add(tag)
        elif key == "ore_data":
            if tag in {"ORE", "DATA"}:
                progress.add(tag)
        elif key == "lux_med":
            if tag in {"LUX", "MED"}:
                progress.add(tag)
        elif key == "port_rep":
            if tag in self.current_port().bonus_tags:
                self.contract_progress[contract.name] += 1
        elif key == "nonpref":
            if tag and tag == self.current_port().penalty_tag:
                self.contract_progress[contract.name] = 1
        elif key == "market_maker":
            if same_turn:
                self.contract_progress[contract.name] = True
        elif key == "expansion":
            self.contract_progress[contract.name] += 1
        elif key == "broker_bonus":
            self.contract_progress[contract.name] = len(self.completed_contracts)

        if self._contract_completed(contract):
            self._complete_contract(contract)

    def _contract_completed(self, contract: ContractCardData) -> bool:
        key = contract.effect_key
        progress = self.contract_progress.get(contract.name)
        if key in {"food_2", "med_2", "ore_2", "parts_2", "data_2", "lux_2"}:
            return progress >= 2
        if key == "mixed_3":
            return len(progress) >= 3
        if key == "bulk_3":
            return progress.get("max", 0) >= 3
        if key == "fast_turn":
            return progress >= 2
        if key in {"lux_data", "parts_ore", "med_food", "ore_data", "lux_med"}:
            return len(progress) >= 2
        if key == "port_rep":
            return progress >= 2
        if key == "nonpref":
            return progress >= 1
        if key == "market_maker":
            return progress is True
        if key == "supplier_loop":
            turns = self.contract_turn_tracker.get(contract.name, set())
            return len(turns) >= 3
        if key == "expansion":
            return progress >= 5
        if key == "broker_bonus":
            return progress >= 2
        return False

    def _complete_contract(self, contract: ContractCardData) -> None:
        self._log(f"계약 완료! {contract.name} 보상 지급")
        self.completed_contracts.append(contract.name)
        self.active_contracts.remove(contract)
        self._apply_contract_reward(contract)
        for active in self.active_contracts[:]:
            if active.effect_key == "broker_bonus":
                self.contract_progress[active.name] = len(self.completed_contracts)
                if self._contract_completed(active):
                    self._complete_contract(active)

    def _apply_contract_reward(self, contract: ContractCardData) -> None:
        key = contract.effect_key
        if key == "food_2":
            self.credits += 8
        elif key == "med_2":
            self.credits += 10
        elif key == "ore_2":
            self.credits += 9
        elif key == "parts_2":
            self.credits += 10
        elif key == "data_2":
            self.credits += 11
        elif key == "lux_2":
            self.credits += 14
        elif key == "mixed_3":
            self.credits += 12
        elif key == "bulk_3":
            self.credits += 15
        elif key == "fast_turn":
            self.credits += 7
            self.fuel += 1
        elif key == "lux_data":
            self.credits += 16
        elif key == "parts_ore":
            self.credits += 12
            self.next_turn_parts_bonus += 1
        elif key == "med_food":
            self.credits += 11
            self.next_turn_intel_bonus += 1
        elif key == "ore_data":
            self.credits += 14
            self._refresh_market_slot(self.market_cargo)
        elif key == "lux_med":
            self.credits += 15
            self.sells_left += 1
        elif key == "port_rep":
            self.credits += 9
            for tag in self.current_port().bonus_tags:
                self.port_bonus_adjust[tag] = self.port_bonus_adjust.get(tag, 0) + 1
        elif key == "nonpref":
            self.credits += 8
        elif key == "market_maker":
            self.credits += 10
        elif key == "supplier_loop":
            self.credits += 18
        elif key == "expansion":
            self.cargo_limit += 1
        elif key == "broker_bonus":
            self.credits += 20

    def _use_port_service(self) -> None:
        port = self.current_port()
        if port.name == "Mining Colony":
            if self.parts >= 1:
                self.parts -= 1
                self._refresh_market_slot(self.market_cargo)
                self._log("서비스 사용: 화물 슬롯 교체")
        elif port.name == "Festival World":
            if self.fuel >= 1:
                self.fuel -= 1
                self.sells_left += 1
        elif port.name == "Medical Hub":
            if self.intel >= 1:
                self.intel -= 1
                self.sell_bonus_first += 3
        elif port.name == "Data Exchange":
            if self.intel >= 2:
                self.intel -= 2
                self._refresh_market_slot(self.market_action)
        elif port.name == "Industrial Shipyard":
            self.action_cost_discount = max(self.action_cost_discount, 2)
            self.action_cost_discount_uses = max(self.action_cost_discount_uses, 1)
        elif port.name == "Agri Ring":
            if self.parts >= 1:
                self.parts -= 1
                self.cargo_limit += 1
        elif port.name == "Luxury Spindle":
            if self.credits >= 2:
                self.credits -= 2
                self.market_scan_active = True
        elif port.name == "Frontier Bazaar":
            if self.fuel >= 1:
                self.fuel -= 1
                self.buys_left += 1

    def _select_best_tag(self) -> str:
        if not self.cargo_bay:
            return self.random.choice(TAGS)
        counts: dict[str, int] = {}
        for cargo in self.cargo_bay:
            counts[cargo.tag] = counts.get(cargo.tag, 0) + 1
        return max(counts, key=counts.get)

    def _clear_reservations(self) -> None:
        for slot in self.market_cargo:
            slot.reserved = False
        for slot in self.market_action:
            slot.reserved = False

    def _boost_contract(self, contract: ContractCardData) -> None:
        key = contract.effect_key
        if key in {"food_2", "med_2", "ore_2", "parts_2", "data_2", "lux_2"}:
            self.contract_progress[contract.name] = self.contract_progress.get(contract.name, 0) + 1
        elif key == "mixed_3":
            progress = self.contract_progress.get(contract.name, set())
            for tag in TAGS:
                if tag not in progress:
                    progress.add(tag)
                    break
            self.contract_progress[contract.name] = progress
        elif key == "bulk_3":
            counts = self.contract_progress.setdefault(contract.name, {"max": 0, "counts": {}})
            pref_tag = next(iter(self.current_port().bonus_tags))
            counts["counts"][pref_tag] = counts["counts"].get(pref_tag, 0) + 1
            counts["max"] = max(counts["max"], counts["counts"][pref_tag])
        elif key in {"lux_data", "parts_ore", "med_food", "ore_data", "lux_med"}:
            progress = self.contract_progress.get(contract.name, set())
            pair_map = {
                "lux_data": ["LUX", "DATA"],
                "parts_ore": ["PARTS", "ORE"],
                "med_food": ["MED", "FOOD"],
                "ore_data": ["ORE", "DATA"],
                "lux_med": ["LUX", "MED"],
            }
            for tag in pair_map[key]:
                if tag not in progress:
                    progress.add(tag)
                    break
            self.contract_progress[contract.name] = progress
        elif key == "port_rep":
            self.contract_progress[contract.name] = self.contract_progress.get(contract.name, 0) + 1
        elif key == "nonpref":
            self.contract_progress[contract.name] = 1
        elif key == "market_maker":
            self.contract_progress[contract.name] = True
        elif key == "expansion":
            self.contract_progress[contract.name] = self.contract_progress.get(contract.name, 0) + 1
        elif key == "broker_bonus":
            self.contract_progress[contract.name] = len(self.completed_contracts)
        if self._contract_completed(contract):
            self._complete_contract(contract)

    def _log(self, message: str) -> None:
        self.log_lines.append(message)


class Scenes:
    mainScene = PortTraderScene()


if __name__ == "__main__":
    window = REMOGame(
        window_resolution=PortTraderScene.SCREEN_SIZE,
        screen_size=PortTraderScene.SCREEN_SIZE,
        fullscreen=False,
        caption="REMO Port Trader",
    )
    window.setCurrentScene(Scenes.mainScene)
    window.run()
