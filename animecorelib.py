import os
import re
import shutil
from collections import defaultdict

# --- 配置区 ---
modpath = "G:\\Steam\\steamapps\\workshop\\content\\1158310\\Vsinger"
dir = "vsinger"
mod_prefix = "vsinger_"

# --- 遗传概率配置 (0-100) ---
N_FATHER_V_MOTHER_FEMALE_CHANCE = 80
N_FATHER_V_MOTHER_MALE_CHANCE = 10
V_FATHER_V_MOTHER_FEMALE_CHANCE = 100
V_FATHER_V_MOTHER_MALE_CHANCE = 20
V_FATHER_N_MOTHER_FEMALE_CHANCE = 30
V_FATHER_N_MOTHER_MALE_CHANCE = 20
# --- 配置区结束 ---

# --- 路径定义 ---
assetpath = os.path.join("gfx", "models", "portraits", "props", dir)
traits_path = os.path.join(modpath, "common", "traits")
accessories_path = os.path.join(modpath, "gfx", "portraits", "accessories")
gene_path = os.path.join(modpath, "common", "genes")
portraits_path = os.path.join(modpath, "gfx", "portraits", "portrait_modifiers")
script_values_path = os.path.join(modpath, "common", "script_values")
script_triggers_path = os.path.join(modpath, "common", "scripted_triggers")
script_effects_path = os.path.join(modpath, "common", "scripted_effects")
localization_path = os.path.join(modpath, "localization", "simp_chinese")
trait_icons_path = os.path.join(modpath, "gfx", "interface", "icons", "traits")

outfit_trigger_file = os.path.join(script_triggers_path, mod_prefix + "portrait_triggers.txt")
inheritance_helpers_file = os.path.join(script_effects_path, mod_prefix + "inheritance_helpers.txt")
lineage_triggers_file = os.path.join(script_triggers_path, mod_prefix + "triggers.txt")
genetic_effects_file = os.path.join(script_effects_path, mod_prefix + "genetic_effects.txt")
localization_file = os.path.join(localization_path, mod_prefix + "l_simp_chinese.yml")
main_traits_file = os.path.join(traits_path, mod_prefix + "traits.txt")

# --- 全局数据结构 ---
lineage_dict = defaultdict(set)
portrait_dict = dict()
all_discovered_traits = set()
code = "utf_8_sig"

def main_handler():
    print("--- Starting Vsinger Mod Script ---")
    
    currentpath = os.path.join(modpath, assetpath)
    for path in [traits_path, accessories_path, gene_path, portraits_path, script_values_path, script_triggers_path, script_effects_path, localization_path, trait_icons_path]:
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
    
    generate_standard_files(currentpath, ddslist)
    print("  > Generated standard portrait files.")

    generate_inheritance_files()
    print("  > Generated inheritance script files with corrected syntax.")
    
    generate_localization_file()
    print("  > Incremental update of localization file complete.")

    update_000_portrait_values(dir)
    print("  > Updated 000_portrait_values.txt.")
    
    print("\nScript finished successfully!")

def generate_standard_files(currentpath, ddslist):
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

def scaffold_trait_definitions():
    # This function remains the same.
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
    flag = vsinger_nation_maid
    requires_trait = vsinger_base
    icon = "{trait}.dds" # Auto-generated icon reference

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

    group = special
    genetic = no
    random_creation = 0
}}
''')

def generate_inheritance_files():
    """
    Generates all inheritance-related script files with corrected syntax.
    """
    lineages = sorted(lineage_dict.keys())
    
    # --- Generate vsinger_triggers.txt ---
    with open(lineage_triggers_file, "w", encoding=code) as f:
        f.write("# Auto-generated by animecorelib.py\n\n")
        
        all_traits = set()
        for traits in lineage_dict.values():
            all_traits.update(traits)
            
        f.write("has_any_vsinger_trait = {\n\tOR = {\n")
        for trait in sorted(list(all_traits)):
            f.write(f"\t\thas_trait = {trait}\n")
        f.write("\t}\n}\n\n")
        
        for lineage, traits in lineage_dict.items():
            f.write(f"has_{lineage}_lineage_trait = {{\n\tOR = {{\n")
            for trait in sorted(list(traits)):
                f.write(f"\t\thas_trait = {trait}\n")
            f.write("\t}\n}\n\n")

    # --- Generate vsinger_inheritance_helpers.txt ---
    with open(inheritance_helpers_file, "w", encoding=code) as f:
        f.write("# Auto-generated by animecorelib.py\n\n")
        
        for lineage, traits in lineage_dict.items():
            f.write(f"vsinger_inherit_{lineage}_lineage_effect = {{\n")
            f.write("\trandom_list = {\n")
            for trait in sorted(list(traits)):
                f.write("\t\t1 = {\n")
                f.write("\t\t\tadd_trait = vsinger_base\n")
                f.write(f"\t\t\tadd_trait = {trait}\n")
                f.write("\t\t\tset_ethnicity = anime_ethnicity\n")
                f.write("\t\t}\n")
            f.write("\t}\n}\n\n")

        f.write("vsinger_inherit_from_parents_effect = {\n")
        f.write("\trandom_list = {\n")
        for lineage in lineages:
            f.write(f"\t\t1 = {{\n")
            f.write(f"\t\t\tweight = {{\n")
            f.write(f"\t\t\t\tvalue = 0\n")
            f.write(f"\t\t\t\tif = {{ limit = {{ mother = {{ has_{lineage}_lineage_trait = yes }} }} add = 100 }}\n")
            f.write(f"\t\t\t\tif = {{ limit = {{ real_father = {{ has_{lineage}_lineage_trait = yes }} }} add = 100 }}\n")
            f.write(f"\t\t\t}}\n")
            f.write(f"\t\t\tvsinger_inherit_{lineage}_lineage_effect = yes\n")
            f.write(f"\t\t}}\n")
        f.write("\t}\n}\n\n")

        f.write("vsinger_inherit_any_lineage_effect = {\n")
        f.write("\trandom_list = {\n")
        for lineage in lineages:
            f.write(f"\t\t1 = {{ vsinger_inherit_{lineage}_lineage_effect = yes }}\n")
        f.write("\t}\n}\n\n")

    # --- Generate vsinger_genetic_effects.txt ---
    with open(genetic_effects_file, "w", encoding=code) as f:
        f.write("# Auto-generated by animecorelib.py\n\n")
        f.write("vsinger_on_birth_set_portrait_effect = {\n")
        f.write("\tif = {\n")
        f.write("\t\tlimit = { specific_waifu_portrait_trigger = no }\n\n")
        f.write("\t\tif = {\n")
        f.write("\t\t\tlimit = {\n")
        f.write("\t\t\t\tOR = {\n")
        f.write("\t\t\t\t\treal_father = { has_any_vsinger_trait = yes }\n")
        f.write("\t\t\t\t\tmother = { has_any_vsinger_trait = yes }\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t}\n\n")
        
        f.write("\t\t\t# N-Father + V-Mother\n")
        f.write("\t\t\tif = {\n")
        f.write("\t\t\t\tlimit = {\n")
        f.write("\t\t\t\t\tNOT = { real_father = { has_any_vsinger_trait = yes } }\n")
        f.write("\t\t\t\t\tmother = { has_any_vsinger_trait = yes }\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t\tif = {\n")
        f.write("\t\t\t\t\tlimit = { is_female = yes }\n")
        f.write(f"\t\t\t\t\trandom = {{\n")
        f.write(f"\t\t\t\t\t\tchance = {N_FATHER_V_MOTHER_FEMALE_CHANCE}\n")
        for i, lineage in enumerate(lineages):
            clause = "if" if i == 0 else "else_if"
            f.write(f"\t\t\t\t\t\t{clause} = {{\n")
            f.write(f"\t\t\t\t\t\t\tlimit = {{ mother = {{ has_{lineage}_lineage_trait = yes }} }}\n")
            f.write(f"\t\t\t\t\t\t\tvsinger_inherit_{lineage}_lineage_effect = yes\n")
            f.write(f"\t\t\t\t\t\t}}\n")
        f.write("\t\t\t\t\t}\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t\telse = {\n")
        f.write(f"\t\t\t\t\trandom = {{\n")
        f.write(f"\t\t\t\t\t\tchance = {N_FATHER_V_MOTHER_MALE_CHANCE}\n")
        for i, lineage in enumerate(lineages):
            clause = "if" if i == 0 else "else_if"
            f.write(f"\t\t\t\t\t\t{clause} = {{\n")
            f.write(f"\t\t\t\t\t\t\tlimit = {{ mother = {{ has_{lineage}_lineage_trait = yes }} }}\n")
            f.write(f"\t\t\t\t\t\t\tvsinger_inherit_{lineage}_lineage_effect = yes\n")
            f.write(f"\t\t\t\t\t\t}}\n")
        f.write("\t\t\t\t\t}\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t}\n")

        f.write("\t\t\t# V-Father + V-Mother\n")
        f.write("\t\t\telse_if = {\n")
        f.write("\t\t\t\tlimit = {\n")
        f.write("\t\t\t\t\treal_father = { has_any_vsinger_trait = yes }\n")
        f.write("\t\t\t\t\tmother = { has_any_vsinger_trait = yes }\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t\tif = {\n")
        f.write("\t\t\t\t\tlimit = { is_female = yes }\n")
        f.write(f"\t\t\t\t\trandom = {{\n")
        f.write(f"\t\t\t\t\t\tchance = {V_FATHER_V_MOTHER_FEMALE_CHANCE}\n")
        f.write(f"\t\t\t\t\t\tvsinger_inherit_from_parents_effect = yes\n")
        f.write(f"\t\t\t\t\t}}\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t\telse = {\n")
        f.write(f"\t\t\t\t\trandom = {{\n")
        f.write(f"\t\t\t\t\t\tchance = {V_FATHER_V_MOTHER_MALE_CHANCE}\n")
        f.write(f"\t\t\t\t\t\tvsinger_inherit_from_parents_effect = yes\n")
        f.write(f"\t\t\t\t\t}}\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t}\n")

        f.write("\t\t\t# V-Father + N-Mother\n")
        f.write("\t\t\telse_if = {\n")
        f.write("\t\t\t\tlimit = {\n")
        f.write("\t\t\t\t\treal_father = { has_any_vsinger_trait = yes }\n")
        f.write("\t\t\t\t\tNOT = { mother = { has_any_vsinger_trait = yes } }\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t\tif = {\n")
        f.write("\t\t\t\t\tlimit = { is_female = yes }\n")
        f.write(f"\t\t\t\t\trandom = {{\n")
        f.write(f"\t\t\t\t\t\tchance = {V_FATHER_N_MOTHER_FEMALE_CHANCE}\n")
        f.write(f"\t\t\t\t\t\tvsinger_inherit_any_lineage_effect = yes\n")
        f.write(f"\t\t\t\t\t}}\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t\telse = {\n")
        f.write(f"\t\t\t\t\trandom = {{\n")
        f.write(f"\t\t\t\t\t\tchance = {V_FATHER_N_MOTHER_MALE_CHANCE}\n")
        f.write(f"\t\t\t\t\t\tvsinger_inherit_any_lineage_effect = yes\n")
        f.write(f"\t\t\t\t\t}}\n")
        f.write("\t\t\t\t}\n")
        f.write("\t\t\t}\n")
        
        f.write("\t\t}\n")
        f.write("\t}\n")
        f.write("}\n")

def generate_localization_file():
    # This function remains the same.
    existing_keys = set()
    if os.path.exists(localization_file):
        with open(localization_file, 'r', encoding=code) as f:
            for line in f:
                match = re.match(r'\s*(\w+):', line)
                if match:
                    existing_keys.add(match.group(1))

    traits_to_append = defaultdict(list)
    for trait in all_discovered_traits:
        key_base = f"trait_{trait}"
        key_desc = f"trait_{trait}_desc"
        key_char_desc = f"trait_{trait}_character_desc"

        if key_base not in existing_keys:
            traits_to_append[trait].append(key_base)
        if key_desc not in existing_keys:
            traits_to_append[trait].append(key_desc)
        if key_char_desc not in existing_keys:
            traits_to_append[trait].append(key_char_desc)

    if not traits_to_append:
        print("  > Localization file is already up-to-date.")
        return
        
    print(f"  > Found traits with missing localization keys. Appending...")

    with open(localization_file, 'a', encoding=code) as f:
        f.write("\n\n# --- Auto-generated by script: New localization entries ---\n")
        for trait, keys_to_add in sorted(traits_to_append.items()):
            try:
                suffix = trait.split('_')[2]
            except IndexError:
                suffix = trait
            
            for key in keys_to_add:
                if key.endswith('_desc') and not key.endswith('_character_desc'):
                    f.write(f' {key}:0 "This character is {suffix}."\n')
                else: # Covers both base trait name and character_desc
                    f.write(f' {key}:0 "{suffix}"\n')
            f.write("\n")

def update_000_portrait_values(dir_name):
    # This function remains the same.
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