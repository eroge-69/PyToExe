import tkinter as tk
from tkinter import ttk, messagebox
import itertools

# Container and pallet definitions
CONTAINERS = {
    "20ft": {"length": 5.90, "width": 2.34, "height": 2.39},
    "40ft": {"length": 12.03, "width": 2.34, "height": 2.39},
    "40ft_hc": {"length": 12.03, "width": 2.34, "height": 2.69},
}

WEIGHT_LIMITS = {
    "China": 25000,
    "Australia": 23500,
    "NZ": 24500,
}

PALLETS = {
    "Naturals 1200": {"weight": 674.76, "length": 1.24, "width": 1.02, "height": 0.742},
    "Naturals HB": {"weight": 1069.56, "length": 1.386, "width": 0.964, "height": 1.054},
    "Naturals 1800": {"weight": 880.08, "length": 1.86, "width": 1.02, "height": 0.685},
    "Naturals HBE": {"weight": 969.94, "length": 1.27, "width": 0.98, "height": 1.03},
}

MAX_STACK_HEIGHT = 3

def try_normal_stacking(pallet, container_length, container_width, container_height):
    L = pallet["length"]
    W = pallet["width"]
    H = pallet["height"]

    # Calculate max layers, ensuring total height does not exceed container height
    max_layers = min(MAX_STACK_HEIGHT, int(container_height // H))
    if max_layers * H > container_height:
        max_layers = max(0, max_layers - 1)

    max_in_length = int(container_length // L)
    max_in_width = int(container_width // W)

    total_pallets = max_in_length * max_in_width * max_layers

    # Prepare matrix layers (L for lengthwise)
    layer = []
    for _ in range(max_in_width):
        row = [f"L" for _ in range(max_in_length)]
        layer.append("/".join(row))

    layers = [layer] * max_layers if max_layers > 0 else []

    return {
        "total_pallets": total_pallets,
        "layers": layers,
        "max_layers": max_layers,
        "pattern": "normal_lengthwise",
    }

def try_alternating_stacking(pallet, container_length, container_width, container_height, weight_limit, pallet_name):
    L = pallet["length"]
    W = pallet["width"]
    H = pallet["height"]
    pallet_weight = pallet["weight"]

    # Calculate max layers, ensuring total height does not exceed container height
    max_layers = min(MAX_STACK_HEIGHT, int(container_height // H))
    if max_layers * H > container_height:
        max_layers = max(0, max_layers - 1)

    # Alternating pattern: Row 1 (W/L/W/L/W), Row 2 (L/W/L/W/L)
    row1_length = 3 * W + 2 * L  # 3 widthwise + 2 lengthwise
    row2_length = 3 * L + 2 * W  # 3 lengthwise + 2 widthwise
    # Total width is sum of max height per row (Row 2 aligns with bottoms of Row 1)
    row1_heights = [L, W, L, W, L]  # Heights (y-direction) for W/L/W/L/W
    row2_heights = [W, L, W, L, W]  # Heights for L/W/L/W/L
    total_width = max(row1_heights) + max(row2_heights)  # e.g., L + W

    # Exceptions for Naturals 1200 and HBE: Allow 10 pallets if length fits, ignore width and weight
    if pallet_name in ["Naturals 1200", "Naturals HBE"]:
        if row1_length <= container_length and row2_length <= container_length:
            pallets_per_layer = 10
            total_pallets = pallets_per_layer * max_layers
            layer = ["W/L/W/L/W", "L/W/L/W/L"]
            layers = [layer] * max_layers if max_layers > 0 else []
            return {
                "total_pallets": total_pallets,
                "layers": layers,
                "max_layers": max_layers,
                "pattern": "alternating",
            }
        return {"total_pallets": 0, "layers": [], "max_layers": 0, "pattern": None}

    # Strict checks for other pallets
    if row1_length > container_length or row2_length > container_length or total_width > container_width:
        return {"total_pallets": 0, "layers": [], "max_layers": 0, "pattern": None}

    pallets_per_layer = 10
    layer_weight = pallets_per_layer * pallet_weight
    max_layer_weight = weight_limit / max_layers if max_layers > 0 else float('inf')

    if layer_weight > max_layer_weight:
        return {"total_pallets": 0, "layers": [], "max_layers": 0, "pattern": None}

    total_pallets = pallets_per_layer * max_layers

    # Matrix layers
    layer = ["W/L/W/L/W", "L/W/L/W/L"]
    layers = [layer] * max_layers if max_layers > 0 else []

    return {
        "total_pallets": total_pallets,
        "layers": layers,
        "max_layers": max_layers,
        "pattern": "alternating",
    }

def try_alternating_1200(pallet, container_length, container_width, container_height, weight_limit, pallet_name):
    L = pallet["length"]
    W = pallet["width"]
    H = pallet["height"]
    pallet_weight = pallet["weight"]

    # Calculate max layers, ensuring total height does not exceed container height
    max_layers = min(MAX_STACK_HEIGHT, int(container_height // H))
    if max_layers * H > container_height:
        max_layers = max(0, max_layers - 1)

    # Use same alternating pattern: W/L/W/L/W, L/W/L/W/L
    row1_length = 3 * W + 2 * L
    row2_length = 3 * L + 2 * W
    row1_heights = [L, W, L, W, L]
    row2_heights = [W, L, W, L, W]
    total_width = max(row1_heights) + max(row2_heights)

    # Exception for Naturals 1200: Allow 10 pallets if length fits, ignore width and weight
    if pallet_name == "Naturals 1200":
        if row1_length <= container_length and row2_length <= container_length:
            pallets_per_layer = 10
            total_pallets = pallets_per_layer * max_layers
            layer = ["W/L/W/L/W", "L/W/L/W/L"]
            layers = [layer] * max_layers if max_layers > 0 else []
            return {
                "total_pallets": total_pallets,
                "layers": layers,
                "max_layers": max_layers,
                "pattern": "alternating_1200",
            }
        return {"total_pallets": 0, "layers": [], "max_layers": 0, "pattern": None}

    # Strict checks (though not used for Naturals 1200)
    if row1_length > container_length or row2_length > container_length or total_width > container_width:
        return {"total_pallets": 0, "layers": [], "max_layers": 0, "pattern": None}

    pallets_per_layer = 10
    layer_weight = pallets_per_layer * pallet_weight
    max_layer_weight = weight_limit / max_layers if max_layers > 0 else float('inf')

    if layer_weight > max_layer_weight:
        return {"total_pallets": 0, "layers": [], "max_layers": 0, "pattern": None}

    total_pallets = pallets_per_layer * max_layers

    # Matrix layers
    layer = ["W/L/W/L/W", "L/W/L/W/L"]
    layers = [layer] * max_layers if max_layers > 0 else []

    return {
        "total_pallets": total_pallets,
        "layers": layers,
        "max_layers": max_layers,
        "pattern": "alternating_1200",
    }

def stack_container(container_type, collections, country, min_pallets=None):
    if isinstance(collections, str):
        collections = [collections]
    else:
        collections = list(collections)

    if min_pallets is None:
        min_pallets = {p: 4 for p in collections}  # Default to 4 pallets per collection
    else:
        # Validate min_pallets
        for p in min_pallets:
            if p not in collections:
                raise ValueError(f"Invalid pallet type: {p}")
        for p in collections:
            if p not in min_pallets:
                min_pallets[p] = 4  # Enforce minimum 4 pallets

    container = CONTAINERS.get(container_type)
    if not container:
        raise ValueError(f"Invalid container type: {container_type}")

    weight_limit = WEIGHT_LIMITS.get(country)
    if not weight_limit:
        raise ValueError(f"Invalid country: {country}")

    # Store configurations for each pallet type
    configs = {}
    for pallet_name in collections:
        if pallet_name not in PALLETS:
            raise ValueError(f"Invalid pallet type: {pallet_name}")
        pallet = PALLETS[pallet_name]
        normal_stack = try_normal_stacking(
            pallet, container["length"], container["width"], container["height"]
        )
        if pallet_name == "Naturals 1200":
            alternating_stack = try_alternating_1200(
                pallet, container["length"], container["width"], container["height"], weight_limit, pallet_name
            )
        else:
            alternating_stack = try_alternating_stacking(
                pallet, container["length"], container["width"], container["height"], weight_limit, pallet_name
            )
        configs[pallet_name] = [
            (normal_stack["total_pallets"], normal_stack["total_pallets"] * pallet["weight"], normal_stack),
            (alternating_stack["total_pallets"], alternating_stack["total_pallets"] * pallet["weight"], alternating_stack),
        ]

    # Check if too many pallets or three or more collections
    too_many_pallets = any(min_pallets[p] > sum(c[0] for c in configs[p]) for p in collections)
    multiple_collections = len(collections) >= 3

    if too_many_pallets or multiple_collections:
        # Collect multiple unique configurations using greedy layer-by-layer approach
        all_configs = []
        config_signatures = set()  # Track unique breakdowns
        max_configs = 5

        # Generate configurations by trying different layer assignments
        for num_layers in range(1, MAX_STACK_HEIGHT + 1):
            for layer_perm in itertools.permutations(collections, num_layers):
                total_pallets = 0
                total_weight = 0
                total_height = 0
                breakdown = {p: 0 for p in collections}
                layers = []
                omitted_collections = {}
                valid = True
                min_requirements_met = True

                for layer_idx, pallet_name in enumerate(layer_perm):
                    best_pattern = None
                    best_pallets = 0
                    best_weight = 0
                    best_stack_info = None

                    for pattern_idx in range(2):
                        config = configs[pallet_name][pattern_idx]
                        pallets, weight, stack_info = config
                        if stack_info["max_layers"] == 0:
                            omitted_collections[pallet_name] = f"No valid stacking pattern for {pallet_name} (dimensions or weight incompatible)"
                            continue
                        pallets_per_layer = pallets // stack_info["max_layers"] if stack_info["max_layers"] > 0 else 0
                        if pallets_per_layer == 0:
                            omitted_collections[pallet_name] = f"No pallets fit in layer for {pallet_name} (dimensions or weight too large)"
                            continue
                        layer_weight = weight // stack_info["max_layers"] if stack_info["max_layers"] > 0 else 0
                        layer_height = PALLETS[pallet_name]["height"]

                        if total_height + layer_height <= container["height"] and total_weight + layer_weight <= weight_limit:
                            if pallets_per_layer > best_pallets:
                                best_pallets = pallets_per_layer
                                best_weight = layer_weight
                                best_stack_info = stack_info
                                best_pattern = pattern_idx

                    if best_pattern is None:
                        valid = False
                        if pallet_name not in omitted_collections:
                            omitted_collections[pallet_name] = f"Could not fit {pallet_name} in layer {layer_idx + 1}"
                        break

                    total_pallets += best_pallets
                    total_weight += best_weight
                    total_height += PALLETS[pallet_name]["height"]
                    breakdown[pallet_name] += best_pallets
                    if best_stack_info["layers"]:
                        layers.append((pallet_name, best_stack_info["pattern"], best_stack_info["layers"][0]))
                    else:
                        layers.append((pallet_name, best_stack_info["pattern"], None))

                for pallet_name in collections:
                    required_min = max(4, min_pallets[pallet_name])
                    if breakdown[pallet_name] < required_min:
                        min_requirements_met = False
                        if breakdown[pallet_name] == 0 and pallet_name not in omitted_collections:
                            omitted_collections[pallet_name] = f"Could not fit {pallet_name} (insufficient pallets: {breakdown[pallet_name]} < {required_min})"

                at_least_one_included = any(breakdown[p] > 0 for p in collections)
                if not at_least_one_included:
                    valid = False
                    for p in collections:
                        if p not in omitted_collections:
                            omitted_collections[p] = f"Could not fit {p} in configuration"

                breakdown_signature = tuple(sorted((p, breakdown[p]) for p in collections))
                if breakdown_signature in config_signatures:
                    continue

                if valid and total_pallets > 0:
                    config = {
                        "total_pallets": total_pallets,
                        "total_weight": total_weight,
                        "breakdown": breakdown,
                        "layers": layers,
                        "pattern": "mixed",
                        "collection": "mixed",
                        "min_requirements_met": min_requirements_met,
                        "omitted_collections": omitted_collections
                    }
                    all_configs.append(config)
                    config_signatures.add(breakdown_signature)

        if not any(config["min_requirements_met"] for config in all_configs):
            current_min_pallets = {p: max(4, min_pallets[p]) for p in collections}
            max_relaxations = 10
            relaxation_step = 0

            while relaxation_step < max_relaxations and not any(config["min_requirements_met"] for config in all_configs):
                relaxation_step += 1
                for p in collections:
                    current_min_pallets[p] = max(0, current_min_pallets[p] - 1)

                for num_layers in range(1, MAX_STACK_HEIGHT + 1):
                    for layer_perm in itertools.permutations(collections, num_layers):
                        total_pallets = 0
                        total_weight = 0
                        total_height = 0
                        breakdown = {p: 0 for p in collections}
                        layers = []
                        omitted_collections = {}
                        valid = True
                        min_requirements_met = True

                        for layer_idx, pallet_name in enumerate(layer_perm):
                            best_pattern = None
                            best_pallets = 0
                            best_weight = 0
                            best_stack_info = None

                            for pattern_idx in range(2):
                                config = configs[pallet_name][pattern_idx]
                                pallets, weight, stack_info = config
                                if stack_info["max_layers"] == 0:
                                    omitted_collections[pallet_name] = f"No valid stacking pattern for {pallet_name} (dimensions or weight incompatible)"
                                    continue
                                pallets_per_layer = pallets // stack_info["max_layers"] if stack_info["max_layers"] > 0 else 0
                                if pallets_per_layer == 0:
                                    omitted_collections[pallet_name] = f"No pallets fit in layer for {pallet_name} (dimensions or weight too large)"
                                    continue
                                layer_weight = weight // stack_info["max_layers"] if stack_info["max_layers"] > 0 else 0
                                layer_height = PALLETS[pallet_name]["height"]

                                if total_height + layer_height <= container["height"] and total_weight + layer_weight <= weight_limit:
                                    if pallets_per_layer > best_pallets:
                                        best_pallets = pallets_per_layer
                                        best_weight = layer_weight
                                        best_stack_info = stack_info
                                        best_pattern = pattern_idx

                            if best_pattern is None:
                                valid = False
                                if pallet_name not in omitted_collections:
                                    omitted_collections[pallet_name] = f"Could not fit {pallet_name} in layer {layer_idx + 1}"
                                break

                            total_pallets += best_pallets
                            total_weight += best_weight
                            total_height += PALLETS[pallet_name]["height"]
                            breakdown[pallet_name] += best_pallets
                            if best_stack_info["layers"]:
                                layers.append((pallet_name, best_stack_info["pattern"], best_stack_info["layers"][0]))
                            else:
                                layers.append((pallet_name, best_stack_info["pattern"], None))

                        for pallet_name in collections:
                            required_min = max(0, current_min_pallets[pallet_name])
                            if breakdown[pallet_name] < required_min:
                                min_requirements_met = False
                                if breakdown[pallet_name] == 0 and pallet_name not in omitted_collections:
                                    omitted_collections[pallet_name] = f"Could not fit {pallet_name} (insufficient pallets: {breakdown[pallet_name]} < {required_min})"

                        at_least_one_included = any(breakdown[p] > 0 for p in collections)
                        if not at_least_one_included:
                            valid = False
                            for p in collections:
                                if p not in omitted_collections:
                                    omitted_collections[p] = f"Could not fit {p} in configuration"

                        breakdown_signature = tuple(sorted((p, breakdown[p]) for p in collections))
                        if breakdown_signature in config_signatures:
                            continue

                        if valid and total_pallets > 0:
                            config = {
                                "total_pallets": total_pallets,
                                "total_weight": total_weight,
                                "breakdown": breakdown,
                                "layers": layers,
                                "pattern": "mixed",
                                "collection": "mixed",
                                "min_requirements_met": min_requirements_met,
                                "omitted_collections": omitted_collections
                            }
                            all_configs.append(config)
                            config_signatures.add(breakdown_signature)

        all_configs.sort(key=lambda x: (
            -sum(1 for p in collections if x["breakdown"][p] > 0),
            -x["total_pallets"]
        ))
        return all_configs[:max_configs] if all_configs else [{"total_pallets": 0, "total_weight": 0, "breakdown": {}, "layers": [], "omitted_collections": {p: "No feasible configuration (check dimensions or constraints)" for p in collections}}]

    best_overall = {
        "total_pallets": 0,
        "total_weight": 0,
        "breakdown": {},
        "layers": [],
        "pattern": None,
        "collection": None,
    }

    for num_layers in range(1, MAX_STACK_HEIGHT + 1):
        for layer_assignments in itertools.product([(p, i) for p in collections for i in range(2)], repeat=num_layers):
            total_pallets = 0
            total_weight = 0
            total_height = 0
            breakdown = {p: 0 for p in collections}
            layers = []
            valid = True
            for pallet_name, pattern_idx in layer_assignments:
                config = configs[pallet_name][pattern_idx]
                pallets, weight, stack_info = config
                if stack_info["max_layers"] == 0:
                    valid = False
                    break
                pallets_per_layer = pallets // stack_info["max_layers"] if stack_info["max_layers"] > 0 else 0
                layer_weight = weight // stack_info["max_layers"] if stack_info["max_layers"] > 0 else 0
                layer_height = PALLETS[pallet_name]["height"]
                total_height += layer_height
                if total_height > container["height"]:
                    valid = False
                    break
                total_pallets += pallets_per_layer
                total_weight += layer_weight
                breakdown[pallet_name] += pallets_per_layer
                if stack_info["layers"]:
                    layers.append((pallet_name, stack_info["pattern"], stack_info["layers"][0]))
                else:
                    layers.append((pallet_name, stack_info["pattern"], None))
                if total_weight > weight_limit:
                    valid = False
                    break
            if valid:
                for pallet_name in collections:
                    if breakdown[pallet_name] < min_pallets[pallet_name]:
                        valid = False
                        break
            if valid and total_pallets > best_overall["total_pallets"]:
                best_overall.update({
                    "total_pallets": total_pallets,
                    "total_weight": total_weight,
                    "breakdown": breakdown,
                    "layers": layers,
                    "pattern": "mixed",
                    "collection": "mixed",
                })

    if best_overall["total_pallets"] == 0:
        return {"total_pallets": 0, "total_weight": 0, "breakdown": {}, "layers": []}

    return best_overall

def print_result(res):
    if isinstance(res, list):
        if not res or res[0]["total_pallets"] == 0:
            output = ["No valid configurations found."]
            if res and res[0].get("omitted_collections"):
                output.append("Reasons for failure:")
                for pallet, reason in res[0]["omitted_collections"].items():
                    output.append(f"  {pallet}: {reason}")
            return "\n".join(output)
        
        output = []
        for idx, config in enumerate(res, 1):
            output.append(f"Configuration {idx}:")
            output.append(f"Total pallets: {config['total_pallets']}")
            output.append(f"Total weight (kg): {config['total_weight']:.2f}")
            output.append(f"Breakdown per collection: {config['breakdown']}")
            output.append(f"Minimum requirements met: {'Yes' if config.get('min_requirements_met', False) else 'No'}")
            output.append(f"Stacking pattern: {config['pattern']}")
            if config.get("omitted_collections"):
                output.append("Omitted collections:")
                for pallet, reason in config["omitted_collections"].items():
                    output.append(f"  {pallet}: {reason}")
            if config["layers"]:
                output.append("Stacking layers:")
                for layer_idx, (pallet_name, pattern, layer) in enumerate(config["layers"], 1):
                    output.append(f" Layer {layer_idx} ({pallet_name}, {pattern}):")
                    if layer:
                        for row in layer:
                            output.append("  " + row)
                    else:
                        output.append("  No matrix available (irregular layout).")
            else:
                output.append("No stacking layers available.")
            output.append("")
        return "\n".join(output)
    
    output = []
    output.append(f"Total pallets: {res['total_pallets']}")
    output.append(f"Total weight (kg): {res['total_weight']:.2f}")
    output.append(f"Breakdown per collection: {res['breakdown']}")
    output.append(f"Stacking pattern: {res['pattern']}")
    if res["layers"]:
        output.append("Stacking layers:")
        for idx, (pallet_name, pattern, layer) in enumerate(res["layers"], 1):
            output.append(f" Layer {idx} ({pallet_name}, {pattern}):")
            if layer:
                for row in layer:
                    output.append("  " + row)
            else:
                output.append("  No matrix available (irregular layout).")
    else:
        output.append("No stacking layers available.")
    return "\n".join(output)

class ContainerStackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Container Stacking Planner")
        self.root.geometry("800x900")  # Increased size to accommodate canvas
        
        # Configure style
        style = ttk.Style()
        style.configure("TLabel", padding=5)
        style.configure("TButton", padding=5)
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        ttk.Label(self.main_frame, text="Container Stacking Planner", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Country selection
        ttk.Label(self.main_frame, text="Select Country").grid(row=1, column=0, sticky=tk.W)
        self.country_var = tk.StringVar(value="China")
        country_combo = ttk.Combobox(self.main_frame, textvariable=self.country_var, values=["China", "Australia", "NZ"], state="readonly")
        country_combo.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Container type selection
        ttk.Label(self.main_frame, text="Select Container Type").grid(row=3, column=0, sticky=tk.W)
        self.container_var = tk.StringVar(value="20ft")
        container_combo = ttk.Combobox(self.main_frame, textvariable=self.container_var, values=["20ft", "40ft", "40ft_hc"], state="readonly")
        container_combo.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Collections selection
        ttk.Label(self.main_frame, text="Select Collections").grid(row=5, column=0, sticky=tk.W)
        self.collection_frame = ttk.Frame(self.main_frame)
        self.collection_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.check_vars = {}
        self.min_entries = {}
        collections = ["Naturals 1200", "Naturals HB", "Naturals 1800", "Naturals HBE"]
        for i, collection in enumerate(collections):
            var = tk.BooleanVar()
            self.check_vars[collection] = var
            chk = ttk.Checkbutton(self.collection_frame, text=collection, variable=var, command=lambda c=collection: self.toggle_min_entry(c))
            chk.grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            
            entry = ttk.Entry(self.collection_frame, width=10)
            entry.insert(0, "4")  # Default to 4 pallets
            entry.configure(state="disabled")
            entry.grid(row=i, column=1, sticky=tk.W)
            self.min_entries[collection] = entry
        
        # Calculate button
        self.calculate_btn = ttk.Button(self.main_frame, text="Calculate Stacking", command=self.calculate)
        self.calculate_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Results area
        self.results_frame = ttk.Frame(self.main_frame)
        self.results_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(self.results_frame, text="Stacking Results", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.output_text = tk.Text(self.results_frame, height=10, width=60, wrap=tk.WORD)
        self.output_text.grid(row=1, column=0, pady=5)
        self.output_text.configure(state="disabled")
        
        # Visualization area
        self.viz_frame = ttk.Frame(self.main_frame)
        self.viz_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        ttk.Label(self.viz_frame, text="Layer Visualization (Top View)", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        # Configuration and layer selection
        self.config_var = tk.StringVar(value="1")
        self.layer_var = tk.StringVar(value="1")
        ttk.Label(self.viz_frame, text="Configuration:").grid(row=1, column=0, sticky=tk.W)
        self.config_combo = ttk.Combobox(self.viz_frame, textvariable=self.config_var, values=["1"], state="readonly", width=10)
        self.config_combo.grid(row=1, column=1, sticky=tk.W)
        self.config_combo.bind("<<ComboboxSelected>>", lambda e: self.update_visualization())
        
        ttk.Label(self.viz_frame, text="Layer:").grid(row=1, column=2, sticky=tk.W)
        self.layer_combo = ttk.Combobox(self.viz_frame, textvariable=self.layer_var, values=["1"], state="readonly", width=10)
        self.layer_combo.grid(row=1, column=3, sticky=tk.W)
        self.layer_combo.bind("<<ComboboxSelected>>", lambda e: self.update_visualization())
        
        # Canvas for drawing
        self.canvas = tk.Canvas(self.viz_frame, width=400, height=200, bg="white", borderwidth=2, relief="groove")
        self.canvas.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Store results for visualization
        self.current_result = None
        self.current_container = None
        self.current_collections = None
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(1, weight=1)
        self.viz_frame.columnconfigure(0, weight=1)
    
    def toggle_min_entry(self, collection):
        entry = self.min_entries[collection]
        if self.check_vars[collection].get():
            entry.configure(state="normal")
        else:
            entry.configure(state="disabled")
            entry.delete(0, tk.END)
            entry.insert(0, "4")  # Default to 4 pallets
    
    def draw_layer(self, config_idx, layer_idx):
        self.canvas.delete("all")
        if not self.current_result or (isinstance(self.current_result, list) and config_idx >= len(self.current_result)):
            self.canvas.create_text(200, 100, text="No configuration available", font=("Arial", 12))
            return
        
        config = self.current_result[config_idx] if isinstance(self.current_result, list) else self.current_result
        if not config.get("layers") or layer_idx >= len(config["layers"]):
            self.canvas.create_text(200, 100, text=f"No layer {layer_idx + 1} in configuration", font=("Arial", 12))
            return

        pallet_name, pattern, layer_matrix = config["layers"][layer_idx]
        container = CONTAINERS[self.current_container]
        pallet = PALLETS[pallet_name]

        # Fixed pixel coordinates (1 meter = 30 pixels)
        canvas_width = 400
        canvas_height = 200
        container_length = container["length"] * 30  # 20ft: 5.90m * 30 = 177
        container_width = container["width"] * 30    # 2.34m * 30 = 70.2
        offset_x = (canvas_width - container_length) / 2  # 20ft: (400 - 177) / 2 ≈ 111.5
        offset_y = (canvas_height - container_width) / 2  # (200 - 70.2) / 2 ≈ 64.9

        # Draw container outline
        self.canvas.create_rectangle(
            offset_x, offset_y, offset_x + container_length, offset_y + container_width,
            outline="black", width=2
        )
        self.canvas.create_text(
            offset_x, offset_y - 10,
            text=f"{self.current_container} (Top View, {pallet_name}, {pattern})",
            font=("Arial", 10)
        )

        # Draw pallets based on pattern
        if pattern == "normal_lengthwise" and layer_matrix:
            max_in_length = int(container["length"] // pallet["length"])  # 20ft, HB: 5.90 / 1.386 = 4
            max_in_width = int(container["width"] // pallet["width"])    # 20ft, HB: 2.34 / 0.964 = 2
            for i in range(max_in_width):
                for j in range(max_in_length):
                    x1 = offset_x + j * pallet["length"] * 30
                    y1 = offset_y + i * pallet["width"] * 30
                    x2 = x1 + pallet["length"] * 30
                    y2 = y1 + pallet["width"] * 30
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", fill="lightblue")
                    self.canvas.create_text(
                        (x1 + x2) / 2, (y1 + y2) / 2,
                        text=f"{pallet_name.split()[1]}\nL",
                        font=("Arial", 8)
                    )

        elif pattern in ["alternating", "alternating_1200"] and layer_matrix:
            # Row 1: W/L/W/L/W
            row1_y = offset_y
            row1_pattern = ["W", "L", "W", "L", "W"]
            x_position = 0
            row1_bottoms = []  # Store bottom y-coordinates for Row 2 alignment
            for j, orientation in enumerate(row1_pattern):
                if orientation == "W":
                    x1 = offset_x + x_position * 30
                    y1 = row1_y
                    x2 = x1 + pallet["width"] * 30
                    y2 = y1 + pallet["length"] * 30
                    x_position += pallet["width"]
                    color = "green"
                    fill = "lightgreen"
                    label = "W"
                    bottom_y = pallet["length"]
                else:  # orientation == "L"
                    x1 = offset_x + x_position * 30
                    y1 = row1_y
                    x2 = x1 + pallet["length"] * 30
                    y2 = y1 + pallet["width"] * 30
                    x_position += pallet["length"]
                    color = "blue"
                    fill = "lightblue"
                    label = "L"
                    bottom_y = pallet["width"]

                self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, fill=fill)
                self.canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=f"{pallet_name.split()[1]}\n{label}",
                    font=("Arial", 8)
                )
                row1_bottoms.append(bottom_y)

            # Row 2: L/W/L/W/L
            row2_pattern = ["L", "W", "L", "W", "L"]
            x_position = 0
            for j, orientation in enumerate(row2_pattern):
                y1 = offset_y + row1_bottoms[j] * 30  # Align with bottom of pallet above
                if orientation == "W":
                    x1 = offset_x + x_position * 30
                    x2 = x1 + pallet["width"] * 30
                    y2 = y1 + pallet["length"] * 30
                    x_position += pallet["width"]
                    color = "green"
                    fill = "lightgreen"
                    label = "W"
                else:  # orientation == "L"
                    x1 = offset_x + x_position * 30
                    x2 = x1 + pallet["length"] * 30
                    y2 = y1 + pallet["width"] * 30
                    x_position += pallet["length"]
                    color = "blue"
                    fill = "lightblue"
                    label = "L"

                self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, fill=fill)
                self.canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=f"{pallet_name.split()[1]}\n{label}",
                    font=("Arial", 8)
                )

        else:
            self.canvas.create_text(200, 100, text="No valid layout for this layer", font=("Arial", 12))

        # Add layer label
        self.canvas.create_text(
            offset_x + container_length / 2, offset_y + container_width + 20,
            text=f"Layer {layer_idx + 1}",
            font=("Arial", 10)
        )

    def update_visualization(self):
        try:
            config_idx = int(self.config_var.get()) - 1
            layer_idx = int(self.layer_var.get()) - 1
            self.draw_layer(config_idx, layer_idx)
        except ValueError:
            self.canvas.delete("all")
            self.canvas.create_text(200, 100, text="Select a valid configuration and layer", font=("Arial", 12))

    def calculate(self):
        try:
            # Get selected values
            country = self.country_var.get()
            container = self.container_var.get()
            collections = [c for c, var in self.check_vars.items() if var.get()]
            min_pallets = {}
            for c in collections:
                value = self.min_entries[c].get()
                try:
                    min_pallets[c] = int(value)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid minimum pallets for {c}. Please enter a valid number.")
                    return
            
            if not collections:
                messagebox.showerror("Error", "Please select at least one collection.")
                return
            
            # Calculate stacking
            self.current_result = stack_container(container, collections, country, min_pallets)
            self.current_container = container
            self.current_collections = collections
            output = print_result(self.current_result)
            
            # Update configuration and layer dropdowns
            if isinstance(self.current_result, list):
                config_count = len(self.current_result)
                self.config_combo["values"] = [str(i) for i in range(1, config_count + 1)]
                if config_count > 0:
                    self.config_var.set("1")
                    layer_count = len(self.current_result[0].get("layers", []))
                    self.layer_combo["values"] = [str(i) for i in range(1, layer_count + 1)]
                    self.layer_var.set("1")
                else:
                    self.config_combo["values"] = ["1"]
                    self.layer_combo["values"] = ["1"]
                    self.config_var.set("1")
                    self.layer_var.set("1")
            else:
                self.config_combo["values"] = ["1"]
                self.layer_combo["values"] = [str(i) for i in range(1, len(self.current_result.get("layers", [])) + 1)]
                self.config_var.set("1")
                self.layer_var.set("1")
            
            # Display results
            self.output_text.configure(state="normal")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, output)
            self.output_text.configure(state="disabled")
            
            # Draw initial visualization
            self.update_visualization()
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating stacking: {str(e)}")
            self.canvas.delete("all")
            self.canvas.create_text(200, 100, text="Error in calculation", font=("Arial", 12))

def main():
    root = tk.Tk()
    app = ContainerStackingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()