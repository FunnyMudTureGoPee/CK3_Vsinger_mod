# Vsinger Mod 自动化工作流指南

## 致谢与说明

本 Mod 的核心肖像系统基于 [二向箔 (Anime Portrait Overhaul)](https://steamcommunity.com/sharedfiles/filedetails/?id=2975613539) 框架及其 `animecorelib.py` 脚本。我们在此对原作者的杰出工作表示最诚挚的敬意和感谢。

本文档 (`vsinger_readme.md`) 主要关注 **Vsinger Mod 自身的自动化工作流程**，特别是如何利用我们改进后的 Python 脚本来快速添加新的角色和特质。

如果您希望深入了解 `二向箔` 框架的底层实现原理、接口细节或手动配置方法，请参阅原始的说明文档：[anime_core_lib_readme.md](./anime_core_lib_readme.md)。

---

## 核心设计思想

本 Mod 的核心设计遵循“**单一数据源**”原则。这意味着，所有与角色特质、系别和继承逻辑相关的信息，都唯一地源自于您在 `gfx/models/portraits/props/vsinger/` 目录下的 **`.dds` 图像文件名**。

您不再需要手动编辑任何与继承逻辑相关的脚本文件。您只需要按照约定的格式命名您的图像文件，然后运行一次 Python 脚本即可。

## 自动化脚本 `animecorelib.py`

位于 Mod 根目录下的 `animecorelib.py` 是整个自动化流程的核心。当您运行此脚本时，它会执行以下操作：

1.  **扫描图像文件**：读取 `gfx/models/portraits/props/vsinger/` 目录下的所有 `.dds` 文件。
2.  **解析文件名**：根据命名约定，从文件名中提取“系别”、“特质名称”等信息。
3.  **自动生成/覆盖以下文件**：
    *   **肖像与换装文件**：所有常规的 `.asset`、`_portraits.txt`、`_props.txt`、`_genes_special_accessories.txt` 等。
    *   `common/scripted_triggers/vsinger_triggers.txt`：自动生成 `has_any_vsinger_trait` 和每个系别的 `has_{lineage}_lineage_trait` 触发器。
    *   `common/scripted_effects/vsinger_inheritance_helpers.txt`：自动为每个系别生成一个 `vsinger_inherit_{lineage}_lineage_effect` 效果，其中包含该系别下所有特质的随机列表。
    *   `common/scripted_effects/vsinger_genetic_effects.txt`：自动生成核心的“母本/父本优先”继承逻辑。
    *   `localization/simp_chinese/vsinger_traits_l_simp_chinese.yml`：为所有发现的特质自动生成占位符本地化条目。
4.  **智能追加特质模板**：
    *   脚本会检查 `common/traits/vsinger_traits.txt` 文件。
    *   如果发现某个在文件名中定义的新特质（例如 `vsinger_miku_兔女郎`）在该文件中不存在，脚本会自动在文件末尾为其**追加**一个基础模板，供您后续填充游戏数值。
    *   此过程是**非破坏性**的，绝不会修改您已有的特质定义。

---

## 如何添加一个新的角色/特质

这是您未来扩展 Mod 时唯一需要遵循的流程。

### 第一步：命名您的图像文件

这是最关键的一步。您的 `.dds` 文件必须遵循以下命名约定：

`vsinger_{系别}_{特质后缀}_{换装编号}_diffuse.dds`

**示例：**

*   文件名: `vsinger_miku_兔女郎_1_diffuse.dds`
    *   **系别**: `miku`
    *   **特质后缀**: `兔女郎`
    *   **换装编号**: `1`
    *   **脚本将生成的特质名称**: `vsinger_miku_兔女郎`

*   文件名: `vsinger_luka_luka_0_diffuse.dds`
    *   **系别**: `luka`
    *   **特质后缀**: `luka`
    *   **换装编号**: `0` (通常用于基础服装)
    *   **脚本将生成的特质名称**: `vsinger_luka_luka`

### 第二步：放置图像文件

将您按照上述约定命名好的 `.dds` 文件放入以下目录：

`Vsinger/gfx/models/portraits/props/vsinger/`

### 第三步：运行自动化脚本

直接在您的终端中运行 `animecorelib.py` 脚本。

```powershell
python.exe animecorelib.py
```

### 第四步 (可选)：自定义特质数值

脚本运行后，会自动在 `Vsinger/common/traits/vsinger_traits.txt` 文件中为您创建或更新特质模板。打开该文件，找到新生成的特质（例如 `vsinger_miku_兔女郎`），并为其填充您期望的游戏数值（例如 `character_modifier`）。

### 第五步 (可选)：更新本地化文本

脚本会在 `Vsinger/localization/simp_chinese/vsinger_traits_l_simp_chinese.yml` 文件中为您创建占位符。打开该文件，将自动生成的文本（例如 `"兔女郎"`）修改为您期望的、更完整的游戏内文本。

---

## 手动维护的文件

以下文件**不会**被脚本完全覆盖，需要您根据需求进行手动维护：

*   `common/scripted_triggers/00_vsinger_triggers.txt`
    *   **用途**：用于存放**静态的、基础的**触发器，例如 `is_vsinger_portrait_trigger`。这些触发器不应被自动化流程所影响。
*   `common/on_action/anime_actions.txt`
    *   **用途**：用于将我们的继承逻辑集成到 `Anime Core Lib` 框架的 `on_birth_child` 事件中。通常情况下，您不需要修改此文件。

通过将手动逻辑和自动逻辑分离，我们确保了工作流程的清晰和稳定。
