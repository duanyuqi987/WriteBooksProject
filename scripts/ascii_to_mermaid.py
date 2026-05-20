#!/usr/bin/env python3
"""Replace ASCII art diagrams with Mermaid.js equivalents - fault tolerant version."""

import re, sys

BOOK_PATH = '/mnt/usvdisk/newData/duanyajun/WriteAIBook/docs/2026-05-16/学习书/robot-arm-control-from-scratch.md'

with open(BOOK_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

replacements_made = 0
skipped = 0

def mermaid(code):
    return f'```mermaid\n{code.strip()}\n```'

def try_replace(name, old, new):
    global content, replacements_made, skipped
    if old in content:
        content = content.replace(old, new)
        replacements_made += 1
        print(f"  ✅ [{replacements_made}] {name}")
        return True
    else:
        skipped += 1
        print(f"  ⚠️  SKIP [{skipped}] {name} — not found in file")
        return False

# ─── 1. 6-axis robot arm structure ───
try_replace("6-axis arm structure",
"""```
                    ┌──────────────┐
                    │   末端执行器   │  ← 第6轴（手腕旋转）
                    │  (夹爪/吸盘)   │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │    第5轴      │  ← 手腕俯仰
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │    第4轴      │  ← 手腕旋转
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │         前臂            │
              └────────────┬────────────┘
                           │
                    ┌──────┴───────┐
                    │    第3轴      │  ← 肘部
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │         上臂            │
              └────────────┬────────────┘
                           │
                    ┌──────┴───────┐
                    │    第2轴      │  ← 肩部俯仰
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │    第1轴      │  ← 腰部旋转
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │         基座            │
              └─────────────────────────┘
```""",
mermaid("""
graph BT
    subgraph 末端区["🎯 末端"]
        J6["第6轴<br/>手腕旋转<br/>(夹爪/吸盘)"]
        J5["第5轴<br/>手腕俯仰"]
        J4["第4轴<br/>手腕旋转"]
    end
    subgraph 手臂区["🦾 手臂"]
        前臂["前臂"]
        J3["第3轴<br/>肘部"]
        上臂["上臂"]
        J2["第2轴<br/>肩部俯仰"]
    end
    subgraph 基座区["⚓ 基座"]
        J1["第1轴<br/>腰部旋转"]
        基座["基座"]
    end
    J6 --> J5 --> J4 --> 前臂 --> J3 --> 上臂 --> J2 --> J1 --> 基座
"""))

# ─── 2. Three-layer architecture ───
try_replace("Three-layer architecture",
"""```
┌──────────────────────────────────────────────────────┐
│                    🔵 主控层                          │
│                                                      │
│   ┌────────────────────────────────────────────┐    │
│   │           上位机 / 工业PC                    │    │
│   │    轨迹规划 | 逆运动学求解 | 碰撞检测         │    │
│   └──────────────────┬─────────────────────────┘    │
│                      │ 轨迹点序列（每 20ms 一个点）     │
│   ┌──────────────────▼─────────────────────────┐    │
│   │             主控制器 MCU                    │    │
│   │        实时轨迹插补 | 指令分发               │    │
│   └──────────────────┬─────────────────────────┘    │
│                      │                               │
└──────────────────────┼───────────────────────────────┘
                       │ 预发参数 + SYNC 同步帧
        ┌──────────────▼──────────────────────────┐
        │              🟡 通信层 CAN Bus            │
        │                                         │
        │  ┌──────────────┐  ┌────────────────┐   │
        │  │  CAN 总线     │  │   应用层协议    │   │
        │  │  差分双绞线   │  │  位置/速度/力矩  │   │
        │  └──────────────┘  └────────────────┘   │
        └──────────────┬──────────────────────────┘
                       │ 广播到全部关节
        ┌──────────────▼──────────────────────────────────┐
        │                  🟢 关节层（每个关节各一套）        │
        │                                                 │
        │  ┌─────────────────────────────────────────┐    │
        │  │              磁编码器                    │    │
        │  │         实时角度反馈（0.1ms 一次）         │    │
        │  └──────────────────┬──────────────────────┘    │
        │                     │                           │
        │  ┌──────────────────▼──────────────────────┐    │
        │  │             关节 MCU                     │    │
        │  │       指令缓存 + 三环 PID 控制器          │    │
        │  └──────────────────┬──────────────────────┘    │
        │                     │ 位置环 → 速度环 → 电流环     │
        │  ┌──────────────────▼──────────────────────┐    │
        │  │         FOC 磁场定向控制                 │    │
        │  │     Clark变换 + Park变换 + SVPWM         │    │
        │  └──────────────────┬──────────────────────┘    │
        │                     │ U/V/W 三相电压              │
        │  ┌──────────────────▼──────────────────────┐    │
        │  │         BLDC/PMSM 无刷电机               │    │
        │  │           带动关节转动                    │    │
        │  └─────────────────────────────────────────┘    │
        └─────────────────────────────────────────────────┘
```""",
mermaid("""
flowchart TB
    subgraph 主控层["🔵 主控层（规划决策）"]
        direction TB
        A1["上位机 / 工业PC<br/>轨迹规划 | 逆运动学求解 | 碰撞检测"]
        A2["主控制器 MCU<br/>实时轨迹插补 | 指令分发"]
        A1 -->|"轨迹点序列<br/>（每20ms一个点）"| A2
    end

    subgraph 通信层["🟡 通信层 CAN Bus"]
        direction LR
        B1["CAN 总线<br/>差分双绞线"]
        B2["应用层协议<br/>位置 / 速度 / 力矩"]
    end

    subgraph 关节层["🟢 关节层（每个关节各一套）×6"]
        direction TB
        C1["磁编码器<br/>实时角度反馈（0.1ms/次）"]
        C2["关节 MCU<br/>指令缓存 + 三环 PID 控制器"]
        C3["FOC 磁场定向控制<br/>Clark变换 + Park变换 + SVPWM"]
        C4["BLDC/PMSM 无刷电机<br/>带动关节转动"]
        C1 --> C2 -->|"位置环→速度环→电流环"| C3 -->|"U/V/W 三相电压"| C4
    end

    主控层 -->|"预发参数 + SYNC 同步帧"| 通信层 -->|"广播到全部关节"| 关节层
"""))

# ─── 3. Magnetic field + wire ───
try_replace("Wire in magnetic field",
"""```
        N极 (上)
        │  │  │  ← 磁力线从N指向S
  ┌─────┼──┼──┼─────┐
  │     │  │  │     │
  │  →  →  →  →  →  │  ← 导线（电流方向→）
  │     │  │  │  F  │  ← 导线受力方向（向外推）
  │     │  │  │     │
  └─────┼──┼──┼─────┘
        │  │  │
        S极 (下)
```""",
mermaid("""
graph TB
    N["N极（上）"] -->|"磁力线 ↓"| WIRE["导线<br/>电流方向 →<br/>F = B·I·L"]
    S["S极（下）"] -->|"磁力线 ↓"| WIRE
    WIRE -->|"受力方向"| FOUT["F（向外推）"]
    style WIRE fill:#ffeb3b,stroke:#333
    style FOUT fill:#4caf50,color:#fff
"""))

# ─── 4. Coil in magnetic field ───
try_replace("Coil rotation force",
"""```
       N极
       │
  ┌────┴────┐
  │  ┌──┐  │  ← 线圈
  │  │  │  │
  │  └──┘  │
  └────┬────┘
       │
       S极

线圈左边：电流↓，磁场→，受力←（向后）
线圈右边：电流↑，磁场→，受力→（向前）
          → 产生一个旋转力矩！
```""",
mermaid("""
graph TB
    subgraph 磁场区["磁极 N→S"]
        N2["N极"]
        S2["S极"]
    end
    subgraph 线圈区["线圈"]
        L["左边: 电流↓ 受力←"]
        R["右边: 电流↑ 受力→"]
    end
    L -->|"力偶"| TORQUE["旋转力矩 τ"]
    R -->|"力偶"| TORQUE
    style TORQUE fill:#ff9800,color:#fff
"""))

# ─── 5. Brushed motor ───
try_replace("Brushed motor structure",
"""```
          ┌──────────────────────────────┐
          │         定子（机壳）          │
          │   ┌───────永磁体─────────┐   │
          │   │  N            S      │   │
          │   │    ┌─────────┐      │   │
          │   │    │  转子    │      │   │
          │   │    │ (线圈组) │      │   │
          │   │    │         │      │   │
          │   │    │   ┌───┐ │      │   │
          │   │    │   │轴 │ │      │   │
          │   │    │   └───┘ │      │   │
          │   │    └────┬────┘      │   │
          │   │         │           │   │
          │   │    ┌────┴────┐      │   │
          │   │    │ 换向器   │      │   │
          │   │    │ (铜片环) │      │   │
          │   │    └────┬────┘      │   │
          │   │         │           │   │
          │   │    ┌────┴────┐      │   │
          │   │    │ 电刷 ×2  │      │   │
          │   │    │ (碳刷)   │      │   │
          │   │    └────┬────┘      │   │
          │   │         │           │   │
          │   └─────────┼───────────┘   │
          │          电源线             │
          └──────────────────────────────┘
```""",
mermaid("""
graph TB
    subgraph 定子["定子（机壳）"]
        MAG["永磁体<br/>N | S"]
        subgraph 转子内部["转子（旋转部分）"]
            COIL["线圈组"]
            SHAFT["输出轴"]
        end
        COMM["换向器<br/>（铜片环）"]
        BRUSH["电刷 ×2<br/>（碳刷）"]
        PWR["电源线"]
    end
    COIL --> SHAFT --> COMM
    COMM -->|"滑动接触"| BRUSH --> PWR
    style BRUSH fill:#f44336,color:#fff
    style COMM fill:#ff9800,color:#fff
"""))

# ─── 6. Brushless motor ───
try_replace("Brushless motor structure",
"""```
          ┌──────────────────────────────┐
          │         定子（铁芯 + 线圈）   │
          │   ┌──┐  ┌──┐  ┌──┐         │
          │   │线│  │线│  │线│         │
          │   │圈│  │圈│  │圈│         │
          │   │A │  │B │  │C │         │
          │   └──┘  └──┘  └──┘         │
          │         ┌────┐             │
          │         │永磁│  ← 转子     │
          │         │体  │             │
          │         │ N/S│             │
          │         └────┘             │
          │            │               │
          │         输出轴             │
          └──────────────────────────────┘
               ↑     ↑     ↑
               A相   B相   C相  （三根线直接接线圈）
```""",
mermaid("""
graph TB
    subgraph 定子固定["定子（铁芯+线圈）静止不动"]
        direction LR
        CA["线圈 A（U相）"]
        CB["线圈 B（V相）"]
        CC["线圈 C（W相）"]
    end
    subgraph 转子旋转["转子（永磁体）旋转"]
        MAG2["永磁体 N/S"]
        SHAFT2["输出轴"]
    end
    CA --- CA_O["A相引出线"]
    CB --- CB_O["B相引出线"]
    CC --- CC_O["C相引出线"]
    MAG2 --> SHAFT2
    style MAG2 fill:#4caf50,color:#fff
    style 定子固定 fill:#e3f2fd
"""))

# ─── 7. Harmonic drive ───
try_replace("Harmonic drive",
"""```
      ┌──────────────────────┐
      │      波发生器        │  ← 椭圆盘，连接电机轴
      │      (椭圆)          │
      └──────────────────────┘
              │
              ▼（压住柔轮）
      ┌──────────────────────┐
      │      柔轮            │  ← 薄壁可变形环，外圈有齿
      │    （Flexspline）     │
      └──────────────────────┘
              │
              ▼（啮合）
      ┌──────────────────────┐
      │      刚轮            │  ← 刚性内齿轮，齿数多2个
      │   （Circular Spline） │
      └──────────────────────┘
```""",
mermaid("""
graph TB
    WG["波发生器<br/>（椭圆盘，连接电机轴）"]
    FS["柔轮 Flexspline<br/>（薄壁可变形环，外圈有齿）"]
    CS["刚轮 Circular Spline<br/>（刚性内齿轮，齿数多2个）"]
    WG -->|"压住"| FS -->|"啮合"| CS
    style WG fill:#2196f3,color:#fff
    style FS fill:#ff9800,color:#fff
    style CS fill:#4caf50,color:#fff
"""))

# ─── 8. FOC translation pipeline ───
try_replace("FOC translation pipeline",
"""```
你想要的效果（转子视角）：
   "产生 0.5 N·m 的转矩"
    → I_q = 0.5 / k_t = 5A（第2章的 k_t=0.1）
    → I_d = 0（不增强也不削弱磁场）
         │
         ▼
┌─────────────────────────────┐
│  第1步：电流环 PID          │  在 d/q 坐标系中做 PID 控制
│  I_d_target=0, I_q_target=5A│
│  → U_d, U_q（d/q轴电压）    │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  第2步：反 Park 变换        │  从旋转坐标系 → 静止坐标系
│  (U_d, U_q) + 转子角度 θ     │
│  → (U_α, U_β)               │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  第3步：SVPWM               │  从两相静止电压 → 三相 PWM 占空比
│  (U_α, U_β)                 │
│  → (D_a, D_b, D_c)          │  (0~1, 对应 0%~100% 占空比)
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  第4步：三相逆变器          │  6 个 IGBT/MOSFET 开关
│  PWM 信号 → U/V/W 三相电压  │
└─────────────┬───────────────┘
              │
              ▼
         【无刷电机】
              │
              ▼
┌─────────────────────────────┐
│  第5步：电流采样 + 编码器   │  反馈回路
│  测量: I_a, I_b, I_c（三相电流）│
│  测量: θ（转子角度）         │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  第6步：Clark + Park 变换   │  从三相电流 → d/q 轴电流
│  (I_a, I_b) + θ → (I_d_fb, I_q_fb) │
└─────────────┬───────────────┘
              │
              ▼
      反馈回第1步的电流环 PID
      （比较目标 I_d/I_q 和实际 I_d_fb/I_q_fb）
```""",
mermaid("""
flowchart TB
    subgraph INTENT["🎯 控制意图（转子视角）"]
        I["产生 0.5 N·m 转矩<br/>→ I_q = 5A, I_d = 0"]
    end

    subgraph FORWARD["⬇️ 前向翻译路径"]
        direction TB
        S1["<b>步骤1: 电流环 PID</b><br/>在 d/q 坐标系中做PID控制<br/>I_d/q_target → U_d, U_q"]
        S2["<b>步骤2: 反 Park 变换</b><br/>旋转坐标系→静止坐标系<br/>(U_d,U_q)+θ → (U_α,U_β)"]
        S3["<b>步骤3: SVPWM</b><br/>两相静止→三相PWM<br/>(U_α,U_β) → (D_a,D_b,D_c)"]
        S4["<b>步骤4: 三相逆变器</b><br/>6个IGBT开关<br/>PWM → U/V/W 三相电压"]
    end

    subgraph FEEDBACK["⬆️ 反馈测量路径"]
        direction TB
        S5["<b>步骤5: 采样</b><br/>I_a, I_b, I_c 三相电流<br/>θ 转子角度（编码器）"]
        S6["<b>步骤6: Clark+Park 变换</b><br/>(I_a,I_b)+θ → (I_d_fb,I_q_fb)"]
    end

    I --> S1 --> S2 --> S3 --> S4 --> MOTOR["⚙️ 无刷电机"]
    MOTOR --> S5 --> S6 -->|"反馈比较"| S1
"""))

# ─── 9. Clark 3-phase geometry ───
try_replace("Clark 3-phase geometry",
"""```
            V相 (120°)
             /
            /    ← I_b（流过V相线圈的电流）
           /
    U相 ──O──── W相 (240°)
     ↑          ↙
   I_a      I_c
   (0°)
```""",
mermaid("""
graph TB
    subgraph 三相["三相线圈空间分布（互差120°）"]
        U["U相 (0°)<br/>电流 I_a"]
        V["V相 (120°)<br/>电流 I_b"]
        W["W相 (240°)<br/>电流 I_c"]
    end
    U --- V --- W --- U
    style U fill:#f44336,color:#fff
    style V fill:#4caf50,color:#fff
    style W fill:#2196f3,color:#fff
"""))

# ─── 10. Alpha-beta coordinate ───
try_replace("Alpha-beta coordinate",
"""```
       β轴 (90°)
        ↑
        │
        │   (I_α, I_β) ← 合成矢量
        │  /
        │ /
        │/
  ──────O──────→ α轴 (0°)
```""",
mermaid("""
graph LR
    O["O（原点）"] --> ALPHA["α轴 (0°)"]
    O --> BETA["β轴 (90°)"]
    O -.->|"合成矢量"| VEC["(I_α, I_β)"]
"""))

# ─── 11. Park transform ───
try_replace("Park transform geometry",
"""```
α-β 静止坐标系              d-q 旋转坐标系（跟着转子转）

    β ↑                        q ↑
      │   ● (I_α, I_β)          │
      │  /  电流矢量             │   ● (I_d, I_q)
      │ /                        │  /  电流矢量在旋转坐标系
      │/                         │ /   下是"静止"的
 ─────O──────→ α         ─────O──────→ d
                                 转子磁场方向
                                 (d轴和磁场方向对齐)
```""",
mermaid("""
flowchart LR
    subgraph 静止系["α-β 静止坐标系<br/>（定子视角）"]
        STAT["电流矢量旋转<br/>→ 交流信号"]
    end
    subgraph 旋转系["d-q 旋转坐标系<br/>（转子视角）"]
        ROT["电流矢量静止<br/>→ 直流信号"]
    end
    静止系 -->|"Park 变换<br/>旋转 -θ"| 旋转系
    style 静止系 fill:#ffebee
    style 旋转系 fill:#e8f5e9
"""))

# ─── 12. SVPWM hexagon ───
try_replace("SVPWM hexagon",
"""```
                V3 (0,1,0)
                    ↑
                   /\\
                  /  \\
          V4     /    \\    V2
      (0,1,1)  /      \\  (1,1,0)
              /        \\
             /     ●    \\        ← 六边形内的任意点都可以
            /  目标矢量  \\         通过相邻两个基本矢量+
           /   (Uα,Uβ)   \\        零矢量组合出来
          /              \\
   V5───┼                ├──── V1(1,0,0)
  (0,0,1)                (1,0,0)
          \\              /
           \\            /
            \\          /
             \\        /
              \\      /
               \\    /
                \\  /
                 V6(1,0,1)
```""",
mermaid("""
graph TB
    subgraph 六边形["SVPWM 空间矢量六边形"]
        V0["V0 零矢量<br/>(0,0,0) / (1,1,1)"]
        V1["V1 (1,0,0) 0°"]
        V2["V2 (1,1,0) 60°"]
        V3["V3 (0,1,0) 120°"]
        V4["V4 (0,1,1) 180°"]
        V5["V5 (0,0,1) 240°"]
        V6["V6 (1,0,1) 300°"]
    end
    TARGET2["🎯 目标矢量 (Uα,Uβ)<br/>通过相邻矢量+零矢量合成"]
    V1 --> V2 --> V3 --> V4 --> V5 --> V6 --> V1
    TARGET2 -.->|"扇区内合成"| V1
    style TARGET2 fill:#ff9800,color:#fff
"""))

# ─── 13. Three-phase inverter ───
try_replace("Three-phase inverter",
"""```
       V_dc（直流母线电压，比如 24V）
        │
  ┌─────┴─────┐
  │           │
  ├──[S1]──[S3]──[S5]──  ← 三个上桥臂开关
  │    │     │     │
  │    ├─ U ─┤─ V ─├─ W   ← 三相输出
  │    │     │     │
  ├──[S2]──[S4]──[S6]──  ← 三个下桥臂开关
  │           │
  └─────┬─────┘
        │
       GND
```""",
mermaid("""
graph TB
    VDC["V_dc<br/>直流母线电压 24V"]
    S1["S1 上桥臂<br/>U相"]
    S3["S3 上桥臂<br/>V相"]
    S5["S5 上桥臂<br/>W相"]
    S2["S2 下桥臂<br/>U相"]
    S4["S4 下桥臂<br/>V相"]
    S6["S6 下桥臂<br/>W相"]
    U_OUT["U相输出"]
    V_OUT["V相输出"]
    W_OUT["W相输出"]
    GND["GND"]

    VDC --> S1 & S3 & S5
    S1 --> U_OUT --> S2 --> GND
    S3 --> V_OUT --> S4 --> GND
    S5 --> W_OUT --> S6 --> GND

    style S1 fill:#4caf50,color:#fff
    style S3 fill:#4caf50,color:#fff
    style S5 fill:#4caf50,color:#fff
    style S2 fill:#f44336,color:#fff
    style S4 fill:#f44336,color:#fff
    style S6 fill:#f44336,color:#fff
"""))

# ─── 14. CAN bus network ───
try_replace("CAN bus network",
"""```
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│关节1 │  │关节2 │  │关节3 │  │ ...  │   ← 6 个关节 MCU
│MCU   │  │MCU   │  │MCU   │  │MCU   │
└──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘
   │         │         │         │
   └─────────┼─────────┼─────────┘
             │         │
       CAN_H ─────────────  ← 双绞线差分信号
       CAN_L ─────────────
             │
        ┌────┴────┐
        │  主控   │
        │  MCU    │
        └─────────┘
```""",
mermaid("""
graph TB
    MAIN2["主控 MCU<br/>（CAN 控制器）"]
    CAN_H["CAN_H 双绞线差分信号"]
    CAN_L["CAN_L 双绞线差分信号"]
    J1_M["关节1 MCU"]
    J2_M["关节2 MCU"]
    J3_M["关节3 MCU"]
    JN_M["关节4~6 MCU"]

    MAIN2 --- CAN_H --- J1_M & J2_M & J3_M & JN_M
    MAIN2 --- CAN_L --- J1_M & J2_M & J3_M & JN_M
"""))

# ─── 15. CAN two-phase protocol ───
try_replace("CAN two-phase protocol",
"""```
主控侧                                CAN 总线                    关节侧
───────                              ─────────                  ───────

准备轨迹点 P_k
  │
  ├─ 帧1: ID=0x101                  ──────────→  关节1 MCU:
  │   Data=[CMD_SET_POS,             CAN_H/CAN_L   缓存 θ1_target
  │          θ1_H, θ1_L]                             等待 SYNC
  │
  ├─ 帧2: ID=0x102                  ──────────→  关节2 MCU:
  │   Data=[CMD_SET_POS,                            缓存 θ2_target
  │          θ2_H, θ2_L]                             等待 SYNC
  │
  ├─ 帧3~6: 类似...                 ──────────→  关节3~6: 同理
  │
  │   ← 此时总线安静了，                      ← 各关节已缓存好参数
  │      全部参数发送完毕                        但还没开始运动
  │
  ├─ 帧7: ID=0x200                  ──────────→  全部 6 个关节:
  │   Data=[SYNC_START]            广播到所有节点   收到 SYNC!
  │                                                同时写入目标值
  │                                                同时启动 FOC 控制
  │
  └─ 等待下一个周期 (20ms 后)         ────────     关节执行中...
```""",
mermaid("""
sequenceDiagram
    participant M as 主控 MCU
    participant CAN as CAN 总线
    participant J1 as 关节1 MCU
    participant J2 as 关节2 MCU
    participant Jn as 关节3~6 MCU

    M->>M: 准备轨迹点 P_k
    M->>CAN: 帧1: ID=0x101<br/>CMD_SET_POS + θ1
    CAN->>J1: 缓存 θ1_target<br/>等待 SYNC
    M->>CAN: 帧2: ID=0x102<br/>CMD_SET_POS + θ2
    CAN->>J2: 缓存 θ2_target<br/>等待 SYNC
    M->>CAN: 帧3~6: ID=0x103~0x106
    CAN->>Jn: 同理缓存参数

    Note over M,Jn: 全部参数发送完毕<br/>各关节已缓存但未执行

    M->>CAN: 帧7: ID=0x200<br/>SYNC_START（广播）
    CAN->>J1: 收到 SYNC!
    CAN->>J2: 收到 SYNC!
    CAN->>Jn: 收到 SYNC!

    Note over J1,Jn: 同时写入目标值<br/>同时启动 FOC 控制

    M->>M: 等待下一个周期 (20ms后)
"""))

# ─── 16. CAN frame structure ───
try_replace("CAN frame structure",
"""```
┌──────┬──────┬──────┬────┬──────┬──────┬─────┬─────┬──────┬──────┐
│ SOF  │ 11位 │ RTR  │ 6位│ DLC  │ 0~8  │ CRC │ ACK │ EOF  │ IFS  │
│ 1bit │  ID  │ 1bit │控制│ 4bit │Bytes │15bit│ 2bit│ 7bit │ 3bit │
└──────┴──────┴──────┴────┴──────┴──────┴─────┴─────┴──────┴──────┘
```""",
mermaid("""
graph LR
    SOF["SOF<br/>1 bit"] --> ID["11位 ID<br/>仲裁优先级"]
    ID --> RTR["RTR 1 bit"]
    RTR --> CTRL["控制 6 bit"]
    CTRL --> DLC["DLC 4 bit<br/>数据长度 0~8"]
    DLC --> DATA["Data 0~8 Bytes<br/>有效载荷"]
    DATA --> CRC["CRC 15 bit"]
    CRC --> ACK["ACK 2 bit"]
    ACK --> EOF["EOF 7 bit"]
    EOF --> IFS["IFS 3 bit"]
    style DATA fill:#4caf50,color:#fff
    style ID fill:#ff9800,color:#fff
"""))

# ─── 17. CAN transceiver wiring ───
try_replace("CAN transceiver wiring",
"""```
MCU（片上CAN控制器）       CAN 收发器（如 SN65HVD230）
┌──────────┐              ┌──────────────┐
│          │     TX       │              │
│  CAN_TX  ├─────────────→│  D           │──→ CAN_H
│          │              │              │
│  CAN_RX  │←─────────────│  R           │──→ CAN_L
│          │              │              │
└──────────┘              └──────────────┘
                           CAN_H 和 CAN_L 之间
                           接 120Ω 终端电阻（两端）
```""",
mermaid("""
graph LR
    subgraph MCU2["MCU（片上CAN控制器）"]
        TX["CAN_TX"]
        RX["CAN_RX"]
    end
    subgraph TRX["CAN 收发器 SN65HVD230"]
        D["D"]
        R_PIN["R"]
    end
    TX -->|"TX"| D
    D -->|"CAN_H"| BUS_H["CAN_H"]
    R_PIN -->|"CAN_L"| BUS_L["CAN_L"]
    RES["120Ω 终端电阻<br/>（总线两端各一）"] -.-> BUS_H
    RES -.-> BUS_L
"""))

# ─── 18. Two-link arm ───
try_replace("Two-link planar arm",
"""```
         y ↑
           │
           │        末端 (x, y)
           │       ●
           │      /
           │  L2 /    ← 第二段连杆，长度 L2
           │    / θ2
           │   ●  ← 关节 2（肘部）
           │  /
           │ / L1      ← 第一段连杆，长度 L1
           │/ θ1
      ─────●─────────→ x
           基座
```""",
mermaid("""
graph LR
    BASE["基座<br/>(0,0)"]
    J1["关节1 θ₁"]
    ELBOW["关节2 θ₂<br/>（肘部）"]
    END_ARM["末端 (x,y)"]
    BASE -->|"L₁ 连杆1长度"| J1
    J1 -->|"L₂ 连杆2长度"| ELBOW
    ELBOW --> END_ARM
    style BASE fill:#795548,color:#fff
    style END_ARM fill:#ff9800,color:#fff
"""))

# ─── 19. Trapezoidal/S-curve ───
try_replace("Trapezoidal velocity profile",
"""```
速度 ↑
     │     ┌─────────┐
     │    /           \\
     │   /             \\
     │  /               \\
     │ /                 \\
     └─┴───────────────────→ 时间
       加速  匀速  减速

位置 ↑
     │           ●（终点）
     │         /
     │       /
     │     /
     │   /
     │ ●（起点）
     └───────────────────→ 时间
```""",
mermaid("""
graph LR
    subgraph 速度曲线["梯形速度-时间曲线"]
        V1["加速段<br/>v = a·t"] --> V2["匀速段<br/>v = v_max"] --> V3["减速段<br/>v = v_max - a·t"]
    end
    subgraph 位置曲线["S型位置-时间曲线"]
        P1["起点 θ_start"] --> P2["平滑过渡"] --> P3["终点 θ_end"]
    end
"""))

# ─── 20. Trapezoidal vs S-curve ───
try_replace("Trapezoidal vs S-curve comparison",
"""```
梯形曲线：                      S曲线：
加速度 ↑                       加速度 ↑
       │                              │
  ┌────┘                    ┌──┐    ┌──┐
  │                         │   \\  /   │
  │                         │    \\/    │
──┴──────→ t              ──┴──────────→ t
  │    ┌────                  │         └──
  └────┘
  突变 → 冲击                  平滑 → 无冲击
```""",
mermaid("""
graph LR
    subgraph 梯形["梯形加速度曲线"]
        T1["加速度突变<br/>→ 机械冲击 ❌"]
    end
    subgraph S型["S曲线 Jerk-Limited"]
        S1["加速度平滑过渡<br/>→ 无冲击 ✅"]
    end
    梯形 -->|"升级改进"| S型
    style 梯形 fill:#ffebee
    style S型 fill:#e8f5e9
"""))

# ─── 21. Triple-loop cascade ───
try_replace("Triple-loop cascade PID",
"""```
                        ┌──────────────────────────────┐
                        │         位置环 PID            │
   θ_target ──→(─)──→  │  输入: θ_target - θ_actual   │
                ↑       │  输出: ω_target (速度指令)    │
                │       └──────────────┬───────────────┘
                │                      │
                │                      ▼
                │       ┌──────────────────────────────┐
                │       │         速度环 PID            │
                │       │  输入: ω_target - ω_actual   │
                │       │  输出: τ_target (转矩指令)    │
                │       └──────────────┬───────────────┘
                │                      │
                │                      ▼
                │       ┌──────────────────────────────┐
                │       │         电流环 PID            │
                │       │  输入: I_target - I_actual   │
                │       │  输出: U_d, U_q (电压指令)    │
                │       └──────────────┬───────────────┘
                │                      │
                │                      ▼
                │       ┌──────────────────────────────┐
                │       │    FOC + 电机 + 减速器       │
                │       │  U_d,U_q → 转矩 → 加速度...  │
                │       └──────────────┬───────────────┘
                │                      │
                │                      ▼
                │       ┌──────────────────────────────┐
                │       │        编码器采样             │
                │       │   测量 θ_actual, ω_actual    │
                └───────┤   反馈回位置环和速度环        │
                        └──────────────────────────────┘
```""",
mermaid("""
flowchart TB
    INPUT["θ_target<br/>目标角度"]

    subgraph 位置环["位置环 PID（50 Hz）"]
        POS["输入: θ_target - θ_actual<br/>输出: ω_target（速度指令）"]
    end

    subgraph 速度环["速度环 PID（200 Hz）"]
        VEL["输入: ω_target - ω_actual<br/>输出: τ_target（转矩指令）"]
    end

    subgraph 电流环["电流环 PID（10 kHz）"]
        CUR["输入: I_target - I_actual<br/>输出: U_d, U_q（电压指令）"]
    end

    subgraph 物理层["FOC + 电机 + 减速器"]
        PLANT["U_d,U_q → 转矩 → 加速度 → 速度 → 位置"]
    end

    FEEDBACK["编码器采样<br/>θ_actual, ω_actual"]

    INPUT --> 位置环 --> 速度环 --> 电流环 --> 物理层 --> FEEDBACK
    FEEDBACK -->|"θ反馈"| 位置环
    FEEDBACK -->|"ω反馈"| 速度环
"""))

# ─── 22. Frequency domain ───
try_replace("Frequency domain layers",
"""```
增益 ↑
     │
     │  电流环（10kHz）
     │  ┌──────────┐
     │  │          │
     │  │  速度环  │
     │  │  (200Hz) │
     │  │  ┌───────┤
     │  │  │位置环  │
     │  │  │(50Hz)  │
     │  │  │        │
     └──┴──┴────────┴─────→ 频率 (Hz)
     10k  200   50
```""",
mermaid("""
graph LR
    subgraph 频域["三环频域分层"]
        direction TB
        CUR_H["电流环<br/>10 kHz<br/>最快"]
        VEL_M["速度环<br/>200 Hz<br/>中层"]
        POS_L["位置环<br/>50 Hz<br/>最慢"]
    end
    CUR_H -->|"快 50 倍"| VEL_M
    VEL_M -->|"快 4 倍"| POS_L
    style CUR_H fill:#4caf50,color:#fff
    style VEL_M fill:#ff9800,color:#fff
    style POS_L fill:#2196f3,color:#fff
"""))

# ─── 23. Feedforward ───
try_replace("Feedforward structure",
"""```
θ_target ──→ 位置环 PID ──→ (+) ──→ 速度环 PID ──→ (+) ──→ 电流环 PID
                             ↑                      ↑
ω_ff ────────────────────────┘                      │
α_ff ──→ k_t/电机惯量 ──────────────────────────────┘
```""",
mermaid("""
graph LR
    TARGET3["θ_target"] --> POS_PID["位置环 PID"] --> SUM1["(+)"] --> VEL_PID["速度环 PID"] --> SUM2["(+)"] --> CUR_PID["电流环 PID"]
    FF_VEL["ω_ff<br/>速度前馈"] --> SUM1
    FF_ACC["α_ff → k_t/J<br/>加速度前馈"] --> SUM2
    style FF_VEL fill:#4caf50,color:#fff
    style FF_ACC fill:#4caf50,color:#fff
"""))

# ─── 24. Homing flowchart ───
try_replace("Homing search flowchart",
"""```
┌─────────────────────────────────────┐
│  发出 HOME_SEARCH 命令              │
│  关节以慢速向负方向电动           │
└────────────────┬────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│  关节触碰机械限位开关              │
│  （一个物理的微动开关或光电开关）  │
└────────────────┬────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│  开关触发 → MCU 记录当前编码器读数 │
│  该读数 = 机械零位 (θ_mech = 0)     │
└────────────────┬────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│  写入 EEPROM，后续所有角度都基于    │
│  此零点计算                         │
└─────────────────────────────────────┘
```""",
mermaid("""
flowchart TD
    A["发出 HOME_SEARCH 命令<br/>关节以慢速向负方向电动"]
    B["关节触碰机械限位开关<br/>（微动开关/光电开关）"]
    C["开关触发<br/>MCU 记录当前编码器读数<br/>该读数 = 机械零位 θ_mech=0"]
    D["写入 EEPROM<br/>后续所有角度基于此零点计算"]
    A --> B --> C --> D
    style C fill:#4caf50,color:#fff
"""))

# ─── 25. Encoder Z signal ───
try_replace("Encoder Z signal diagram",
"""```
      A 信号: ┌─┐  ┌─┐  ┌─┐  ┌─┐  ┌─┐  ┌─┐
      ───────┘  └──┘  └──┘  └──┘  └──┘  └──┘  └─────

      B 信号:    ┌─┐  ┌─┐  ┌─┐  ┌─┐  ┌─┐  ┌─┐
      ──────────┘  └──┘  └──┘  └──┘  └──┘  └──┘  └──

      Z 信号:                          ┌─┐
      ─────────────────────────────────┘  └───────────
                                        ↑
                                   一圈一个索引脉冲
```""",
mermaid("""
graph TB
    subgraph 编码器["磁编码器三相信号"]
        A_SIG["A 信号: 增量脉冲<br/>（每转 N 个）"]
        B_SIG["B 信号: 与A差90°<br/>（判断方向）"]
        Z_SIG["Z 信号: 每转1个<br/>（索引脉冲）"]
    end
    A_SIG --- B_SIG --- Z_SIG
    Z_SIG -->|"用于"| HOME2["零点标定基准"]
    style Z_SIG fill:#f44336,color:#fff
    style HOME2 fill:#4caf50,color:#fff
"""))

# ─── 26. Eye-in-hand ───
try_replace("Eye-in-hand configuration",
"""```
配置 A：眼在手上（Eye-in-Hand）

相机固定在机械臂末端执行器上

      末端执行器
           ↑
         [相机]  ←── 坐标系：Camera Frame
           ↑
       ┌───┴───┐
       │ 关节5 │
       └───┬───┘
           │
         ... 机械臂 ...
           │
       ┌───┴───┐
       │ 基座  │  ←── 坐标系：Base Frame
       └───────┘

求解：{}^{end}T_{camera}  (末端→相机)
或：   {}^{base}T_{camera} = {}^{base}T_{end} \\cdot {}^{end}T_{camera}
```""",
mermaid("""
graph TB
    subgraph EIH["配置 A：眼在手上 Eye-in-Hand"]
        direction TB
        CAM_EIH["📷 相机<br/>Camera Frame"]
        END_EIH["末端执行器"]
        ARM_EIH["... 机械臂 ..."]
        BASE_EIH["基座<br/>Base Frame"]
    end
    CAM_EIH --- END_EIH --- ARM_EIH --- BASE_EIH
    END_EIH -.->|"待求: end_T_camera"| CAM_EIH
"""))

# ─── 27. Eye-to-hand ───
try_replace("Eye-to-hand configuration",
"""```
配置 B：眼在手外（Eye-to-Hand）

相机固定在机械臂基座或墙壁上，看着机械臂工作区

    ┌──────[相机]  ←── 坐标系：Camera Frame
    │
 ┌──┴──┐
 │基座 │  ←── 坐标系：Base Frame
 └──┬──┘
    │
  ...机械臂...
    │
  末端

求解：{}^{base}T_{camera}  (基座→相机)
```""",
mermaid("""
graph TB
    subgraph ETH["配置 B：眼在手外 Eye-to-Hand"]
        direction TB
        CAM_ETH["📷 相机<br/>Camera Frame<br/>（固定在工作区上方）"]
        BASE_ETH["基座<br/>Base Frame"]
        ARM_ETH["... 机械臂 ..."]
        END_ETH["末端"]
    end
    CAM_ETH --- BASE_ETH --- ARM_ETH --- END_ETH
    BASE_ETH -.->|"待求: base_T_camera"| CAM_ETH
"""))

# ─── 28. Full pipeline knowledge graph ───
try_replace("Full pipeline knowledge graph",
"""```
                      ┌──────────────────────┐
                      │     你的第一个任务    │
                      │ "抓到桌上的螺丝"     │
                      └──────────┬───────────┘
                                 │
                      ┌──────────▼───────────┐
                      │   第7章：轨迹规划+IK  │ ← 从"想去哪"到"怎么转"
                      │   第12章：全链路集成  │
                      └──────────┬───────────┘
                                 │
                      ┌──────────▼───────────┐
                      │   第6章：CAN 总线通信 │ ← 指令怎么传到关节
                      └──────────┬───────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│   第3章：PID 控制  │  │  第8章：三环 PID  │  │   第9章：零点标定  │
│   第2章：电机入门  │  │ 第4章：FOC 控制   │  │  第10章：运动学标定│
│                   │  │ 第5章：坐标变换+SVPWM│ │  第11章：手眼标定  │
└───────────────────┘  └───────────────────┘  └───────────────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                      ┌──────────▼───────────┐
                      │     ✅ 任务完成       │
                      │  末端精确到达目标     │
                      │  误差 < ±0.5mm       │
                      └──────────────────────┘
```""",
mermaid("""
flowchart TB
    TASK["🎯 你的第一个任务<br/>「抓到桌上的螺丝」"]
    PLAN_CH["第7章：轨迹规划+IK<br/>从「想去哪」到「怎么转」"]
    CAN_CH["第6章：CAN 总线通信<br/>指令怎么传到关节"]

    subgraph 执行与标定["三路并行的执行与标定"]
        direction LR
        CTRL_A["第2-3章：电机+PID<br/>第8章：三环 PID"]
        CTRL_B["第4-5章：FOC+坐标变换<br/>Clark/Park/SVPWM"]
        CALIB["第9-11章：三次标定<br/>零点/运动学/手眼"]
    end

    DONE["✅ 任务完成<br/>末端精确到达目标<br/>误差 < ±0.5mm"]

    TASK --> PLAN_CH --> CAN_CH --> 执行与标定 --> DONE
    style TASK fill:#ff9800,color:#fff
    style DONE fill:#4caf50,color:#fff
"""))

# ─── Write back ───
with open(BOOK_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n{'='*50}")
print(f"✅ Replaced: {replacements_made}")
print(f"⚠️  Skipped: {skipped}")
print(f"📏 File size: {len(content)} characters")
