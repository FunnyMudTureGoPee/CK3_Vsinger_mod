import os
import re
from collections import defaultdict

# --- Configuration ---
# Please ensure these paths are correct for your environment
modpath = "G:\\Steam\\steamapps\\workshop\\content\\1158310\\Vsinger"
dir = "vsinger" # The subfolder inside gfx/models/portraits/props/
mod_prefix = "vsinger_"
# --- End of Configuration ---

# Define paths
assetpath = os.path.join("gfx", "models", "portraits", "props", dir)
traits_path = os.path.join(modpath, "common", "traits")
accessories_path = os.path.join(modpath, "gfx", "portraits", "accessories")
gene_path = os.path.join(modpath, "common", "genes")
portraits_path = os.path.join(modpath, "gfx", "portraits", "portrait_modifiers")
script_values_path = os.path.join(modpath, "common", "script_values")
script_triggers_path = os.path.join(modpath, "common", "scripted_triggers")
script_effects_path = os.path.join(modpath, "common", "scripted_effects")
localization_path = os.path.join(modpath, "localization", "simp_chinese")

# Define specific output file paths
outfit_trigger_file = os.path.join(script_triggers_path, mod_prefix + "portrait_triggers.txt")
inheritance_helpers_file = os.path.join(script_effects_path, mod_prefix + "inheritance_helpers.txt")
lineage_triggers_file = os.path.join(script_triggers_path, mod_prefix + "triggers.txt")
genetic_effects_file = os.path.join(script_effects_path, mod_prefix + "genetic_effects.txt")
localization_file = os.path.join(localization_path, mod_prefix + "traits_l_simp_chinese.yml")
main_traits_file = os.path.join(traits_path, mod_prefix + "traits.txt")

# Data structures
lineage_dict = defaultdict(set)
portrait_dict = dict()
all_discovered_traits = set()
code = "utf_8_sig"

def main_handler():
    """
    Main handler to generate all necessary script files based on DDS filenames.
    """
    print("--- Starting Vsinger Mod Script ---")
    
    currentpath = os.path.join(modpath, assetpath)
    for path in [traits_path, accessories_path, gene_path, portraits_path, script_values_path, script_triggers_path, script_effects_path, localization_path]:
        os.makedirs(path, exist_ok=True)
        
    ddslist = os.listdir(currentpath)

    print("--- Analyzing filenames...")
    for file in ddslist:
        if file.endswith('_diffuse.dds'):
            try:
                name = file[:-12]
                parts = name.split('_')
                
                if len(parts) < 4:
                    print(f"Warning: Skipping file with unexpected format: {file}")
                    continue

                lineage = parts[1]
                trait_suffix = parts[2]
                skin_index = int(parts[-1])
                
                trait_name = f"{mod_prefix}{lineage}_{trait_suffix}"
                all_discovered_traits.add(trait_name)
                lineage_dict[lineage].add(trait_name)
                
                if skin_index != 0 and skin_index != 99:
                    if trait_name not in portrait_dict or portrait_dict[trait_name] < skin_index:
                        portrait_dict[trait_name] = skin_index
            except (ValueError, IndexError) as e:
                print(f"Error processing file {file}: {e}. Please check naming convention.")
    
    print(f"--- Analysis complete. Found {len(lineage_dict)} lineages and {len(all_discovered_traits)} unique traits.")

    scaffold_trait_definitions()
    print("  > Scaffolding for missing traits complete.")

    print("--- Generating script files...")
    
    with open(os.path.join(portraits_path, f"{dir}_portraits.txt"), "w", encoding=code) as output_portraits, \
         open(os.path.join(currentpath, f"00_{mod_prefix}{dir}.asset"), "w", encoding=code) as output_asset, \
         open(os.path.join(accessories_path, f"{dir}_props.txt"), "w", encoding=code) as output_props, \
         open(os.path.join(script_values_path, f"{dir}_portrait_values.txt"), "w", encoding=code) as output_values, \
         open(os.path.join(gene_path, f"{dir}_genes_special_accessories.txt"), "w", encoding=code) as output_accessories, \
         open(outfit_trigger_file, "w", encoding=code) as output_nums:

        output_portraits.write(f"{dir}_portrait = {{\n\tportrait_group = anime")
        output_accessories.write("special_genes = {\n\taccessory_genes = {\n\t\tportrait_group = anime")

        id_counter = 0
        slices = 1
        propgroup = f'{dir}_props_{slices}'
        output_accessories.write(f'\n\t\t{propgroup} = {{\n\t\t\tgroup = anime_portrait_group')

        for file in ddslist:
            if file.endswith('_diffuse.dds'):
                try:
                    name = file[:-12]
                    parts = name.split('_')
                    if len(parts) < 4: continue
                    
                    lineage = parts[1]
                    trait_suffix = parts[2]
                    skin_index = int(parts[-1])
                    trait_name = f"{mod_prefix}{lineage}_{trait_suffix}"

                    id_counter += 1
                    if id_counter == 256:
                        id_counter = 1
                        slices += 1
                        propgroup = f'{dir}_props_{slices}'
                        output_accessories.write(f'\n\t\t}}\n\t\t{propgroup} = {{\n\t\t\tgroup = anime_portrait_group')
                    
                    output_portraits.write(f'''
\t{name} = {{
\t\tdna_modifiers = {{
\t\t\taccessory = {{
\t\t\t\tmode = add
\t\t\t\tgene = {propgroup}
\t\t\t\ttemplate = {name}
\t\t\t\tvalue = 1
\t\t\t}}
\t\t}}
\t\tweight = {{
\t\t\tbase = 0
\t\t\tmodifier = {{
\t\t\t\tadd = 200
\t\t\t\thas_trait = {trait_name}''')
                    if skin_index == 0:
                        output_portraits.write('''\n\t\t\t\tshow_default_portrait = yes''')
                    else:
                        output_portraits.write(f"\n\t\t\t\tvar:portrait_index ?= {skin_index}")
                    output_portraits.write('''
\t\t\t\tnormal_portrait_blocked_trigger = no
\t\t\t}
\t\t}
\t}''')
                    output_accessories.write(f'''
\t\t\t{name} = {{
\t\t\t\tindex = {id_counter}
\t\t\t\tanime_male = {{ 1 = {name} }}
\t\t\t\tanime_female = anime_male
\t\t\t\tanime_boy = anime_male
\t\t\t\tanime_girl = anime_male
\t\t\t}}''')
                    output_props.write(f'{name} = {{ portrait_group = anime entity = {{ required_tags = "" node = "bn_h_head_mid" entity = "{name}_entity" }} }}\n')
                    output_asset.write(f'''pdxmesh = {{
\tname = "{name}_mesh"
\tfile = "hm_prophet.mesh"
\tscale = 1.6
\tmeshsettings = {{
\t\tname = "prophet_shieldShape"
\t\tindex = 0
\t\ttexture_diffuse = "{name}_diffuse.dds"
\t\ttexture_specular = "{name}_diffuse.dds"
\t\tshader = "portrait_attachment_alpha_to_coverage"
\t\tshader_file = "gfx/hmportrait.shader"
\t}}
}}
entity = {{
\tname = "{name}_entity"
\tpdxmesh = "{name}_mesh"
}}
''')

                except (ValueError, IndexError):
                    continue

        output_accessories.write("\n\t\t}\n\t}\n}\n")
        output_portraits.write("\n}\n")

        maxportrait = max(portrait_dict.values()) if portrait_dict else 0
        for i in range(maxportrait, 0, -1):
            output_nums.write(f"{mod_prefix}portrait_num_{i} = {{\n\tOR = {{")
            traits_for_num = [trait for trait, num in portrait_dict.items() if num == i]
            if traits_for_num:
                for trait in traits_for_num:
                    output_nums.write(f"\n\t\thas_trait = {trait}")
            else:
                output_nums.write("\n\t\talways = no")
            output_nums.write("\n\t}\n}\n")
        
        output_values.write(f"# Generated portrait max values for {dir}\n")
        output_values.write(f"{dir}_max_portrait = {{\n")
        if maxportrait > 0:
            for i in range(maxportrait, 0, -1):
                if i == maxportrait:
                    output_values.write(f'\tif = {{ limit = {{ {mod_prefix}portrait_num_{i} = yes }} value = {i} }}\n')
                else:
                    output_values.write(f'\telse_if = {{ limit = {{ {mod_prefix}portrait_num_{i} = yes }} value = {i} }}\n')
        output_values.write('\telse = {\n\t\tvalue = 0\n\t}\n}\n')

    print("  > Generated standard portrait files.")

    generate_inheritance_files()
    print("  > Generated inheritance script files.")
    
    generate_localization_file()
    print("  > Generated localization file.")

    update_000_portrait_values(dir)
    print("  > Updated 000_portrait_values.txt.")

def scaffold_trait_definitions():
    """
    Checks for missing trait definitions and appends a template for them.
    """
    existing_traits = set()
    trait_file_pattern = re.compile(r'(\w+)\s*=\s*{')
    
    if os.path.exists(traits_path):
        for filename in os.listdir(traits_path):
            if filename.endswith(".txt"):
                with open(os.path.join(traits_path, filename), 'r', encoding=code) as f:
                    content = f.read()
                    found_traits = trait_file_pattern.findall(content)
                    existing_traits.update(found_traits)

    missing_traits = all_discovered_traits - existing_traits
    
    if not missing_traits:
        print("  > All trait definitions already exist.")
        return

    print(f"  > Found {len(missing_traits)} missing trait definitions. Appending to {os.path.basename(main_traits_file)}...")
    
    with open(main_traits_file, 'a', encoding=code) as f:
        f.write("\n\n# --- Auto-generated by script: Please fill in details ---\n")
        for trait in sorted(list(missing_traits)):
            f.write(f'''
{trait} = {{
    is_good = yes
    flag = vsinger_nation_maid # TODO: You might want to change this
    requires_trait = vsinger_base
    icon = "cm_hand.dds" # TODO: Change icon if needed

    character_modifier = {{
        # TODO: Add character modifiers here
    }}

    desc = {{
        first_valid = {{
            triggered_desc = {{
                trigger = {{ NOT = {{ exists = this }} }}
                desc = trait_{trait}_desc
            }}
            desc = trait_{trait}_character_desc
        }}
    }}

    # opposites = {{ ... }}
    group = special
    genetic = no
    random_creation = 0
}}
''')

def generate_inheritance_files():
    """
    Generates all inheritance-related script files.
    """
    # Generate vsinger_triggers.txt
    with open(lineage_triggers_file, "w", encoding=code) as f:
        f.write("# Auto-generated by animecorelib.py\n\n")
        
        all_traits = set()
        for traits in lineage_dict.values():
            all_traits.update(traits)
            
        f.write("has_any_vsinger_trait = {\n\tOR = {\n")
        for trait in sorted(list(all_traits)):
            f.write(f"\t\thas_trait = {trait}\n")
        f.write("\t}\n}\n\n")
        
        for lineage, traits in sorted(lineage_dict.items()):
            f.write(f"has_{lineage}_lineage_trait = {{\n\tOR = {{\n")
            for trait in sorted(list(traits)):
                f.write(f"\t\thas_trait = {trait}\n")
            f.write("\t}\n}\n\n")

    # Generate vsinger_inheritance_helpers.txt
    with open(inheritance_helpers_file, "w", encoding=code) as f:
        f.write("# Auto-generated by animecorelib.py\n\n")
        
        for lineage, traits in sorted(lineage_dict.items()):
            f.write(f"vsinger_inherit_{lineage}_lineage_effect = {{\n")
            f.write("\trandom_list = {\n")
            for trait in sorted(list(traits)):
                f.write("\t\t1 = {\n")
                f.write("\t\t\tadd_trait = vsinger_base\n")
                f.write(f"\t\t\tadd_trait = {trait}\n")
                f.write("\t\t\tset_ethnicity = anime_ethnicity\n")
                f.write("\t\t}\n")
            f.write("\t}\n}\n\n")

    # Generate vsinger_genetic_effects.txt
    with open(genetic_effects_file, "w", encoding=code) as f:
        f.write("# Auto-generated by animecorelib.py\n\n")
        f.write("vsinger_on_birth_set_portrait_effect = {\n")
        f.write("\t# As per README.md, check if a specific portrait is already assigned\n")
        f.write("\tif = {\n")
        f.write("\t\tlimit = { specific_waifu_portrait_trigger = no }\n\n")
        f.write("\t\t# Check if any parent has a Vsinger trait to trigger inheritance\n")
        f.write("\t\tif = {\n")
        f.write("\t\t\tlimit = {\n")
        f.write("\t\t\t\tOR = {\n")
        f.write("\t\t\t\t\treal_father = { has_any_vsinger_trait = yes }\n")
        f.write("\t\t\t\t\tmother = { has_any_vsinger_trait = yes }\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t}\n\n")
        f.write("\t\t\trandom = {\n")
        f.write("\t\t\t\tchance = 100 # Always attempt inheritance if conditions met\n\n")
        f.write("\t\t\t\t# Mother priority inheritance\n")
        f.write("\t\t\t\tif = {\n")
        f.write("\t\t\t\t\tlimit = { mother = { has_any_vsinger_trait = yes } }\n")
        
        lineages = sorted(lineage_dict.keys())
        for i, lineage in enumerate(lineages):
            clause = "if" if i == 0 else "else_if"
            f.write(f"\t\t\t\t\t{clause} = {{\n")
            f.write(f"\t\t\t\t\t\tlimit = {{ mother = {{ has_{lineage}_lineage_trait = yes }} }}\n")
            f.write(f"\t\t\t\t\t\tvsinger_inherit_{lineage}_lineage_effect = yes\n")
            f.write(f"\t\t\t\t\t}}\n")

        f.write("\t\t\t\t}\n")
        f.write("\t\t\t\t# Father priority inheritance (if mother has no Vsinger traits)\n")
        f.write("\t\t\t\telse_if = {\n")
        f.write("\t\t\t\t\tlimit = { real_father = { has_any_vsinger_trait = yes } }\n")

        for i, lineage in enumerate(lineages):
            clause = "if" if i == 0 else "else_if"
            f.write(f"\t\t\t\t\t{clause} = {{\n")
            f.write(f"\t\t\t\t\t\tlimit = {{ real_father = {{ has_{lineage}_lineage_trait = yes }} }}\n")
            f.write(f"\t\t\t\t\t\tvsinger_inherit_{lineage}_lineage_effect = yes\n")
            f.write(f"\t\t\t\t\t}}\n")
        
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t}\n")
        f.write("\t\t}\n")
        f.write("\t}\n")
        f.write("}\n")

def generate_localization_file():
    """
    Generates a placeholder localization file for the new traits.
    """
    with open(localization_file, "w", encoding=code) as f:
        f.write("l_simp_chinese:\n")
        for trait in sorted(list(all_discovered_traits)):
            try:
                suffix = trait.split('_')[2]
                f.write(f' trait_{trait}:0 "{suffix}"\n')
                f.write(f' trait_{trait}_desc:0 "This character is {suffix}."\n')
                f.write(f' trait_{trait}_character_desc:0 "{suffix}"\n')
            except IndexError:
                f.write(f' trait_{trait}:0 "{trait}"\n')

def update_000_portrait_values(dir_name):
    """
    Update 000_portrait_values.txt to include the new portrait group.
    This function is now idempotent.
    """
    file_path = os.path.join(script_values_path, "000_portrait_values.txt")
    trigger_name = dir_name + "_portrait_trigger"
    value_name = dir_name + "_max_portrait"
    
    try:
        with open(file_path, "r", encoding=code) as f:
            content = f.read()
    except FileNotFoundError:
        content = '''# number of portraits of a character
portrait_max = {
\t# place portrait groups here
\telse = {
\t\tvalue = 0
\t}
}
# initialization of portrait max values
'''

    else_pattern = r"(\n\s*else\s*=\s*{\s*\n\s*value\s*=\s*0\s*\n\s*})"
    init_pattern = r"(#\s*initialization of portrait max values\s*\n)"
    
    new_else_if_block = f'''\telse_if = {{
\t\tlimit = {{
\t\t\t{trigger_name} = yes
\t\t}}
\t\tvalue = {value_name}
\t}}'''

    if f'{trigger_name} = yes' not in content:
        content = re.sub(else_pattern, new_else_if_block + r"\1", content, 1)
    
    if f'{value_name} = 0' not in content:
        content = re.sub(init_pattern, r"\1" + f"{value_name} = 0\n", content, 1)
    
    with open(file_path, "w", encoding=code) as f:
        f.write(content)

if __name__ == "__main__":
    main_handler()
    print("\nScript finished successfully!")