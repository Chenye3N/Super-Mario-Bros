# Sprite 切图流水线

把 `Assets/Sources/SuperMarioBors.png` 按图纸自带的 25 个分区（每个分区有白色 1px 边框 + 白色标题文字）切成单张 sprite，
输出到 `Assets/Sprites/<分区>/<分区>_NN.png`，每张 PNG 都带一份可直接被 Unity 使用的 `.meta`。

## 结果

- 289 张 sprite，25 个分区目录，原尺寸（未缩放、未压缩、未加边距），裁剪到内容外接矩形。
- `.meta`：`textureType: Sprite (8)`、`spriteMode: 1`（Single）、`spritePixelsToUnits: 32`、
  `filterMode: 0`（Point）、`textureCompression: 0`、关闭 mipmap、关闭 fallback physics shape。
- `sprites_index.json` 记录每张图的源图坐标与尺寸；`contact/<分区>.png` 是逐分区的对照图（2 倍放大）。

## 算法

1. **内容掩码**（`slice.py: content_mask`）——`alpha > 0` 就是内容；再剔除两类干扰：
   - 分区边框：连通域的上边和左边一整条都是纯白（正是 1px 矩形框）→ 剔除；
   - 分区标题文字：纯白、`h <= 13`、`w <= 60`，且 2px 环内没有非白像素 → 剔除。
     （水波纹里的白色缺口、云朵、蘑菇斑点会因为相邻有深色像素而保留。）
2. **XY 切分**（`slice3.py: xycut`）——先按整行空白切横带，再在带内按整列空白切，递归到不能再切；对动画网格最有效。
3. **连通域细化**（`slice3.py: refine`）——切完仍含多个物体的块，用 8 连通标记分出物体：
   - 只有一个包围盒"包含"另一个时才合并（白色身体套在 1px 描边里 = 同一个 sprite，例如 Blooper）；
   - 小于整体 2% 的碎片不单独成块，而是并给它中心所在的那个物体；
   - 占比够大的两个物体保持分开（云朵 vs 山丘、藤蔓 vs 平台）。
4. **阅读顺序**——按 y 分带（阈值 = 0.5 × 中位高度）再按 x 排序，`_NN` 编号即行列顺序。
5. **导出**（`publish.py`）——清空 `Assets/Sprites` 后重建，按 `Assets/Sources/SuperMarioBors.png.meta`
   的设置模板生成单张 sprite 的 `.meta`（guid = 资源相对路径的 md5，稳定可复现）。

## 重新运行

```powershell
$py = 'C:\Users\SuperCowHorse\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
cd 'D:\Unity\Super Mario Bros\Tools'
& $py slice3.py        # 切图 → out3/ + out3/manifest.json，并打印每个分区的 lost 校验（应为 0）
& $py qa_contacts.py   # 逐分区对照图 → contact/
& $py publish.py       # 写入 Assets/Sprites（注意：需完全访问权限，见下）
```

`lost` 是"没有被任何矩形覆盖的内容像素数"，全部为 0 表示没有丢像素。

## 已知取舍

- `Castle`(287x378)、`BowserCastle`(177x178)、`CommonObjects_25`(城堡+旗+星) 是整张图一块，没有更细的空白可切。
- `OutsideScenery_05`、`HelpfulObjects_04` 里的小云/小色块和主体像素相连，无法只靠空白分离。
- 背景色分区（Outside / Under Water / Inside）输出的是纯色块，可直接当调色板用。

## 环境备注

`Assets` 目录不在 DSH 沙箱的可写范围内（只有工作区根被标记为可写），因此 `publish.py`
需要用完全访问权限执行一次；此前的 ACL 修复记录在 `D:\Unity\acl-repair-supermario\`。
`_scratch/` 保留探索阶段的探针脚本与中间图，可随时删除。
