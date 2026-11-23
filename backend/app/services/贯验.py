from app.db import 连接
from app.seed import 此刻


def 跑贯验() -> dict:
    """行程账与刷卡点互证：每笔已成对行程对应两笔已成对刷卡；旁路/开腿命运自洽。"""
    conn = 连接()
    try:
        问题 = []
        刷卡数 = conn.execute("SELECT COUNT(*) FROM 刷卡点").fetchone()[0]
        行程 = conn.execute("SELECT * FROM 行程账 WHERE 状态='已成对'").fetchall()
        开腿数 = conn.execute("SELECT COUNT(*) FROM 开腿账 WHERE 状态='在途'").fetchone()[0]
        旁路数 = conn.execute("SELECT COUNT(*) FROM 旁路匣").fetchone()[0]

        for t in 行程:
            进 = conn.execute(
                "SELECT * FROM 刷卡点 WHERE 事件编号=?", (t["进站事件编号"],)
            ).fetchone()
            出 = conn.execute(
                "SELECT * FROM 刷卡点 WHERE 事件编号=?", (t["出站事件编号"],)
            ).fetchone()
            if not 进 or not 出:
                问题.append(f"行程{t['行程键']}缺刷卡点")
                continue
            if 进["命运"] != "已成对" or 出["命运"] != "已成对":
                问题.append(f"行程{t['行程键']}刷卡命运非已成对")
            if 进["行程键"] != t["行程键"] or 出["行程键"] != t["行程键"]:
                问题.append(f"行程{t['行程键']}刷卡行程键不一致")
            if 进["卡号"] != t["卡号"] or 出["卡号"] != t["卡号"]:
                问题.append(f"行程{t['行程键']}卡号不一致")
            if 进["方向"] != "进站" or 出["方向"] != "出站":
                问题.append(f"行程{t['行程键']}方向不配对")

        成对刷 = conn.execute(
            "SELECT COUNT(*) FROM 刷卡点 WHERE 命运='已成对'"
        ).fetchone()[0]
        if 成对刷 != len(行程) * 2:
            问题.append(f"已成对刷卡{成对刷} ≠ 行程{len(行程)}×2")

        开腿刷 = conn.execute(
            "SELECT COUNT(*) FROM 刷卡点 WHERE 命运='已开腿'"
        ).fetchone()[0]
        if 开腿刷 != 开腿数:
            问题.append(f"已开腿刷卡{开腿刷} ≠ 在途开腿{开腿数}")

        # 孤儿出站（口径=当场旁路终态）：旁路行与刷卡命运同成败，禁止无开腿落行程
        孤儿匣 = conn.execute(
            "SELECT * FROM 旁路匣 WHERE 原因='出站孤儿'"
        ).fetchall()
        孤儿数 = len(孤儿匣)
        for 匣 in 孤儿匣:
            刷 = conn.execute(
                "SELECT * FROM 刷卡点 WHERE 事件编号=?", (匣["事件编号"],)
            ).fetchone()
            if not 刷:
                问题.append(f"孤儿{匣['事件编号']}有旁路行无刷卡点")
                continue
            if 刷["命运"] != "已旁路" or 刷["行程键"] != "":
                问题.append(f"孤儿{匣['事件编号']}刷卡命运非已旁路终态")
            双落 = conn.execute(
                "SELECT 1 FROM 行程账 WHERE 出站事件编号=? LIMIT 1", (匣["事件编号"],)
            ).fetchone()
            if 双落:
                问题.append(f"孤儿{匣['事件编号']}旁路与行程双落")
        # 反向核查：已旁路的出站刷卡必须能在旁路匣找到归宿
        旁路出站 = conn.execute(
            "SELECT 事件编号 FROM 刷卡点 WHERE 方向='出站' AND 命运='已旁路'"
        ).fetchall()
        for r in 旁路出站:
            在匣 = conn.execute(
                "SELECT 1 FROM 旁路匣 WHERE 事件编号=? LIMIT 1", (r["事件编号"],)
            ).fetchone()
            if not 在匣:
                问题.append(f"出站{r['事件编号']}已旁路却无旁路匣行")

        通过 = 1 if not 问题 else 0
        说明 = "行程账与刷卡点互证通过" if 通过 else "；".join(问题)[:800]
        conn.execute(
            """INSERT INTO 行程贯验(时刻,刷卡数,行程数,开腿数,旁路数,是否通过,说明)
               VALUES (?,?,?,?,?,?,?)""",
            (此刻(), 刷卡数, len(行程), 开腿数, 旁路数, 通过, 说明),
        )
        conn.commit()
        return {
            "是否通过": bool(通过),
            "刷卡数": 刷卡数,
            "行程数": len(行程),
            "开腿数": 开腿数,
            "旁路数": 旁路数,
            "孤儿出站数": 孤儿数,
            "说明": 说明,
            "问题": 问题,
        }
    finally:
        conn.close()
