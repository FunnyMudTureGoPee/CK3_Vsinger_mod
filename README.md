# 二向箔

## 介绍
在Crusader Kings III实现2D肖像的解决方案和接口。

~~类似技术适用于同代jomini引擎的其他Paradox游戏。~~其他游戏请参考1.14Archive分支。  

## 软件架构
二向箔技术主要包括以下部分：

屏蔽原版模型

创建纸片模型

将平面图像做成纸片模型

调用纸片模型

## 使用说明
本模组的载入标志是`exists = global_var:anime_core_loaded`

推荐使用本模组作为前置模组而非直接复制内容，在`descriptor.mod`文件中加入以下条目以指定载入顺序：
```
dependencies={
	"模组名称（不是路径）"
}
```
本模组提供python脚本以快速处理文件，但仍推荐阅读本文了解运行原理。

本模组所称“纸片人”是指用于模板匹配的一系列条件语句的集合，譬如“一个纸片人C具有n套换装”。

标志某个纸片人C的是特质T，那么我们不关注游戏中有多少个人物具有特质T，所有具有特质T的人物都被认为是纸片人C。


### 快速教程
在本模组中搜索dummy并将相应文件的.info后缀删除以尝试使用，这些文件也包含具体的操作指导。

（推荐）为你的模组在`common/on_action/`设置载入标志，可参考本模组的该文件夹。
#### 加入肖像
对于增加新的肖像，你需要：
1. （推荐）在`gfx/models/props/`中新建文件夹，将不同内容分开。每个文件夹都需要复制一份hm_prophet.mesh。

2. 在前述文件夹（或`gfx/models/props/`，下同）中放置你的图片文件，支持dds和png格式。

   - 推荐使用dds（`DXT5 ARGB 8 bpp | interpolated alpha`）（可以在英伟达官网获得适用于PhotoShop的DDS插件，需要注册）。
   - 推荐大小1024*1024像素，建议头部（若有）位于九宫格正上方格的中间偏下部分，预设的mesh文件焦点为肖像正中，由上至下20%高度。
   - 需要设置Alpha通道，限定图片的哪些部分会被显示，如果使用png文件则无需此步，因为png自带Alpha通道。

3. 在前述文件夹中为你的图片文件注册asset，包括`mesh`和`entity`（并将两者绑定）。

4. 在`common/genes/`中以`special_genes/accessory_genes`形式创建模板。

5. 在`gfx/portraits/accessories/`中将`entity`绑定到模板。

6. 在`gfx/portraits/portrait_modifiers/`中指定模板的应用条件。

   - **不应当使用争夺载入优先度或覆盖的方式处理兼容问题**
   - 无对特定肖像覆盖的需求的绑定逻辑（如特质、变量等）肖像统一使用一致权重200
   - 通用逻辑（文化等）权重应低于绑定逻辑，即权重低于200

7. 参考`common/scripted_triggers/000_2d_portraits.txt`，设置你的`scripted_trigger`（你加入的肖像trigger的具体内容不要写在这个文件里），并issue、pull request或在工坊评论区告知该trigger的名字、换装value（见下）、你的模组的载入标志，我们会将其加入API中。  
你的trigger应该包含（覆盖）所有你加入模板的条件。

8. 所有生成或转化的纸片人必须立即执行`set_ethnicity = anime_ethnicity`，或在生成指令中指明`ethnicity = anime_ethnicity`，以正确处理肖像逻辑。历史纸片人必须**指定**`ethnicity = anime_ethnicity`，因为死后不会执行指令。  

9. 由于种族机制的代码限制，如果你加入的是通过特质等方式绑定的，而非使用类似原版逻辑的权重值肖像，务必确定你的模组如何处理新生儿的肖像问题，否则你会得到空气肖像。  
   - 具有不同基因组的种族杂交会产生不可预见的混乱，为解决此问题，本模组已内置纸片人与非纸片人杂交时设置子代肖像参数为非纸片人一侧的功能，你可以另外加入action来实现你自己的处理逻辑，或直接设置生殖隔离。  
   - 但双亲均为纸片人时没有合适的复制对象，**务必自己设计相关逻辑**。
   - 这里给出一些参考方案，对杂交和双亲纸片人均可考虑使用。
     - 通过出生action分配/抽选特质等绑定
     - 设计生殖隔离（强制流产/不可育等，实现简单）
     - 使用`set_ethnicity`设置为其他种族，但考虑到种族不是对象，此法兼容性较低，尤其是在全面转换类模组环境中你设置的种族可能不存在。
     - 为解决上述问题，本模组预留了`set_muggle_ethnicity`接口，供兼容补丁使用。若你想使用`use_dummy_portrait_inheritance`方案，请联系作者将条件加入其中。
     - 采用类原版策略分配立绘（采用此策略须声明！在`waifu_portrait_trigger`内注册你的缺省条件，在`specific_waifu_portrait_trigger`内注册你的绑定条件）
       - 通过设置一组备份立绘，供未指定的角色使用
       - 直接容许匹配失败时随机抽选立绘（基因的机制是取权重最高者，多个最高权重则在其中随机选择）。出于兼容性考虑，建议仍通过某种方式（如文化）标识之

10.  （若不使用遗传设计则跳过本节） 关于遗传学：`yuri_on_birth_child`是[婚舰通用库](https://steamcommunity.com/sharedfiles/filedetails/?id=3009113176)中模拟生育的action，与原版`on_birth_child`作用域一致，均为新生儿且提供`scope:father`、`scope:mother`和`scope:real_father`。

#### 加入换装
在`common/script_values/`中为你的每个纸片人设置换装数（n-1），建议采用的打包方式是为拥有相同数量换装的纸片人设置`scripted_trigger`，然后逐数量if赋值，但请加上你模组的前缀以避免重名冲突。

### 接口一览 interfaces
#### scripted_trigger （无参数，人物域）
##### waifu_portrait_trigger
使用2D肖像的角色。
用于兼容性互认和消除3D动画等，由于目前CK3没有读取角色ethnicity的功能，所有按前述操作处理的模板条件均应注册到这个接口，**确保此接口与使用2D肖像互为充要条件**（ethnicity为`anime_ethnicity`或其他使用2D肖像的ethnicity，或使用人类下的旧接口）。  

##### specific_waifu_portrait_trigger
使用绑定机制立绘的角色，`waifu_portrait_trigger`的子集。

##### use_anime_ethnicity
临时接口，使用新机制二向箔的角色，是`waifu_portrait_trigger`的子集。  
由于旧版本二向箔仅发布存档不再维护，新引入的模组将只能使用新接口。

##### use_dummy_portrait_inheritance
使用遗传保底接口的角色，是`use_anime_ethnicity`的子集。
接入此接口的纸片人在其孩子的双亲均为`use_anime_ethnicity`时执行`set_muggle_ethnicity`以免出现异常虚空人。

##### normal_portrait_blocked_trigger
用于覆盖`waifu_portrait_trigger`。如果该项为真，则其他不满足此条件的模板不会显示，从而提供一种覆盖特定角色的方法。 不要滥用这个接口，只在你确定要覆盖某个模板的情况下使用。

##### can_change_clothes_by_player_trigger
用于设置角色是否允许被当前玩家通过按钮更改换装，玩家`scope:player`

由游戏规则设置，默认为真。与本模组相关的规则请在分类`categories`中增加`waifu`。

##### anime_core_loaded （全局）
用于在**游戏中**检查是否载入了二向箔。

样例见`scripted_guis\`和`gui\`。

如果你想在你的模组里加入未载入二向箔的警告，将`common\scripted_guis\front_main_sguis.txt`、`gui\scripted_widgets\anime_scripted_widgets.txt.backup`、`gui\anime_dependency.gui.backup`和`gui\anime_trayer.gui.backup`复制到你的模组中并删除`.backup`。

#### scripted_effect （无参数，人物域）
##### set_muggle_ethnicity
用于纸片人相关新生儿的处理。  
此接口预留以供魔幻类等删除原版种族或添加非人种族的模组兼容使用。

##### anime_on_birth_child_specific_portrait
新生儿立绘分配接口，统一在此执行立绘分配。  
每个接入的效果**必须**在最外层用`specific_waifu_portrait_trigger = 0`判断是否已有立绘，有则跳过。

##### anime_on_birth_child_fallback_portrait
新生儿肖像重置接口，用于解决缺失立绘及现版本杂交基因组缺失导致的奇行种问题。
每个接入的效果**必须**在最外层用`specific_waifu_portrait_trigger = 0`判断是否已有立绘，有则跳过。

#### script_value （人物域）
##### portrait_max
可选换装数量（实际具有的换装数量-1），你可以将多个模板设置为一套换装，这些模板应当共享除了换装代码段（见`gfx/portraits/portrait_modifiers/`的.info文件）以外的全部条件，而换装代码段中指定其换装号（以`var:portrait_index`实现），共`max_portrait+1`个模板

#### variable （人物域）
##### portrait_index
数值型
换装号。该变量不存在或超过`portrait_max`时应显示第一张换装肖像。

##### block_normal_portrait
布尔型
有此变量时不执行常规肖像分配，允许使用理发店自选。

#### global_variable
##### safety_mode_on
原版的`should_show_nudity`安全模式仅适用于显示部分，对于非纯立绘的部分该条件使用（如换装上限、音频等）。

推荐使用`exists = global_var:safety_mode_on`作为安全模式。

考虑到大部分模组不含如此过激的内容，本模组目前不提供实现以免挤占互动或决议界面。

#### customizable_localization
我不可能玩过所有二刺螈游戏，所以如果你有更好的命名或者发现以下内容有缺漏，请指正。

##### GetWaifuType
纸片人的类型，如战舰少女。
##### GetOathedWaifuType
誓约（通常是一种脚本关系，类似情人）后对纸片人的称呼，如婚舰、誓约对象等。
##### GetPlayerTitleOfWaifuType
纸片人对玩家的称呼，如各模组原作游戏里的玩家头衔。

#### 其他
游戏规则 `waifu_sexuality_distribution` 和 `husubando_sexuality_distribution`提供了一种覆盖原版性取向分布的功能  
该规则的生效方式是覆盖原版`heterosexuality_chance`等数值。  
注意：对于生成的角色，这个规则不会直接生效，需要在生成后追加`game_rule_sexuality_distribution_reroll_effect = yes` 
如果需要对特定角色指定性取向，则无需加入此条。

### 注意事项
- 在分配立绘绑定标志（如特质等）之前一定要检查`specific_waifu_portrait_trigger = no`，分配标志时一定要同时执行`set_ethnicity = anime_ethnicity`。
- 出于兼容性考虑，如果使用非绑定条件，**避免**使用与文化完全无关的组合条件，以免发生交叉。文化与其他条件组合是没有问题的。
- 通用条件的权重应低于绑定条件。
