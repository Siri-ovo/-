from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Iterable
from pathlib import Path

from src.crawler.clean_jobs import clean_file
from src.crawler.ncss_crawler import crawl_keywords
from src.rag.build_index import build_index


BATCHES: list[tuple[str, list[str]]] = [
    (
        "general_roles",
        ["实习生", "管培生", "助理", "专员", "工程师", "教师", "运营", "销售", "客服", "行政", "人事", "财务", "会计", "市场", "新媒体", "电商"],
    ),
    (
        "it_roles",
        ["软件开发", "Java", "Python", "前端", "后端", "测试", "运维", "网络安全", "数据分析", "算法", "人工智能", "大模型", "嵌入式", "产品经理", "UI", "实施"],
    ),
    (
        "business_roles",
        ["银行", "证券", "保险", "审计", "法务", "采购", "供应链", "物流", "外贸", "跨境电商", "翻译", "文案", "商务", "客户经理"],
    ),
    (
        "engineering_roles",
        ["机械", "电气", "自动化", "电子", "通信", "土木", "建筑", "造价", "材料", "化工", "生物", "制药", "质量", "生产"],
    ),
    (
        "education_health",
        ["心理", "心理咨询", "医生", "护士", "药师", "康复", "影像", "教育", "培训", "课程顾问", "辅导老师", "幼师"],
    ),
    (
        "media_design",
        ["设计", "平面设计", "视觉设计", "视频剪辑", "摄影", "动画", "游戏", "策划", "编导", "直播", "主播"],
    ),
    (
        "majors",
        ["软件工程", "计算机", "数据科学", "物联网", "信息管理", "工商管理", "市场营销", "英语", "汉语言", "会计学", "财务管理", "金融学", "法学", "电子商务"],
    ),
    (
        "english_tech",
        ["SQL", "Excel", "CAD", "PLC", "Linux", "C++", "Go", "PHP", "Vue", "React", "Spring", "Pandas", "AutoCAD", "SolidWorks"],
    ),
    (
        "site_latest",
        [""],
    ),
    (
        "campus_terms",
        ["校招", "应届生", "毕业生", "见习", "储备干部", "管理培训生", "校园招聘", "培训生"],
    ),
    (
        "service_roles",
        ["酒店", "旅游", "餐饮", "门店", "店员", "导购", "美容", "健身", "房产", "物业", "前台", "接待"],
    ),
    (
        "public_admin",
        ["政府", "事业单位", "社工", "社区", "党建", "档案", "文员", "秘书", "办公室", "公共管理"],
    ),
    (
        "environment_food",
        ["农业", "园林", "环境", "环保", "食品", "检测", "水利", "地理信息", "测绘", "安全员"],
    ),
    (
        "advanced_tech",
        ["云计算", "大数据", "区块链", "机器人", "无人机", "芯片", "半导体", "集成电路", "光伏", "新能源", "汽车", "智能制造"],
    ),
    (
        "medical_long_tail",
        ["临床", "医药代表", "医学检验", "口腔", "中医", "公卫", "营养", "实验员", "护理", "健康管理"],
    ),
    (
        "content_language",
        ["俄语", "日语", "韩语", "直播运营", "内容运营", "短视频", "社群", "广告", "品牌", "公关"],
    ),
    (
        "english_long_tail",
        ["AI", "ML", "NLP", "Android", "iOS", ".NET", "C#", "Node", "Docker", "Kubernetes", "TensorFlow", "PyTorch", "Hadoop", "Spark"],
    ),
    (
        "role_suffixes",
        ["经理", "顾问", "代表", "讲师", "研究员", "助教", "技师", "技术员", "操作工", "检验员", "设计师", "分析师", "咨询师", "规划师", "研究助理"],
    ),
    (
        "operations_sales",
        ["运营助理", "电商运营", "新媒体运营", "用户运营", "活动运营", "销售代表", "销售工程师", "客户代表", "招商", "渠道", "售前", "售后"],
    ),
    (
        "finance_legal",
        ["出纳", "税务", "投资", "风控", "信贷", "理财", "证券分析", "法律", "知识产权", "合规", "律师助理"],
    ),
    (
        "research_lab",
        ["科研助理", "研发", "工艺", "实验室", "试剂", "化验", "病理", "生物信息", "药物研发", "医疗器械"],
    ),
    (
        "construction_more",
        ["施工", "监理", "结构", "BIM", "暖通", "给排水", "电力", "预算员", "资料员", "安装"],
    ),
    (
        "education_more",
        ["班主任", "教务", "学管师", "招生", "语文老师", "数学老师", "英语老师", "物理老师", "化学老师"],
    ),
]


BAD_MARKERS = ("???", "??", "����", "�")


def is_corrupt(record: dict) -> bool:
    text = " ".join(str(record.get(key, "")) for key in ("keyword", "job_name", "company_name", "description"))
    return any(marker in text for marker in BAD_MARKERS)


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    return records


def record_key(record: dict) -> str:
    return str(record.get("job_id") or record.get("source_url") or "").strip()


def write_records(path: Path, records: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def merge_batch(raw_path: Path, batch_path: Path) -> tuple[int, int, int, int]:
    existing = load_records(raw_path)
    cleaned_existing = [record for record in existing if record_key(record) and not is_corrupt(record)]
    seen = {record_key(record) for record in cleaned_existing}
    added = 0
    skipped_duplicate = 0
    skipped_bad = 0

    for record in load_records(batch_path):
        key = record_key(record)
        if not key:
            skipped_bad += 1
            continue
        if is_corrupt(record):
            skipped_bad += 1
            continue
        if key in seen:
            skipped_duplicate += 1
            continue
        cleaned_existing.append(record)
        seen.add(key)
        added += 1

    total = write_records(raw_path, cleaned_existing)
    return added, total, skipped_duplicate, skipped_bad


def backup_once(path: Path) -> None:
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak_before_expand")
        if not backup.exists():
            shutil.copy2(path, backup)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/raw/ncss_jobs_raw.jsonl")
    parser.add_argument("--clean", default="data/processed/ncss_jobs_clean.jsonl")
    parser.add_argument("--store", default="vector_store")
    parser.add_argument("--batch-dir", default="data/raw/batches")
    parser.add_argument("--pages", type=int, default=8)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.15)
    parser.add_argument("--stop-after-zero", type=int, default=3)
    parser.add_argument("--start-batch", default="", help="Resume from this batch name.")
    parser.add_argument("--max-batches", type=int, default=0, help="Optional cap for one run.")
    parser.add_argument("--clean-only", action="store_true", help="Remove corrupt rows and rebuild clean data/index only.")
    args = parser.parse_args()

    raw_path = Path(args.raw)
    clean_path = Path(args.clean)
    batch_dir = Path(args.batch_dir)
    backup_once(raw_path)
    backup_once(clean_path)

    if args.clean_only:
        kept = [record for record in load_records(raw_path) if record_key(record) and not is_corrupt(record)]
        total = write_records(raw_path, kept)
        cleaned = clean_file(raw_path, clean_path)
        indexed = build_index(clean_path, Path(args.store))
        print(f"raw_rewritten {total} jobs")
        print(f"cleaned {cleaned} jobs")
        print(f"indexed {indexed} jobs")
        return

    zero_streak = 0
    batch_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []

    started = not args.start_batch
    ran_batches = 0
    stopped_by_limit = False
    for batch_name, keywords in BATCHES:
        if not started:
            started = batch_name == args.start_batch
        if not started:
            continue
        if args.max_batches and ran_batches >= args.max_batches:
            print(f"stop_reason max_batches={args.max_batches}")
            break
        output = batch_dir / f"ncss_jobs_list_batch_20260704_{batch_name}.jsonl"
        print(f"batch_start {batch_name} keywords={len(keywords)}")
        try:
            crawled = crawl_keywords(
                keywords=keywords,
                pages=args.pages,
                limit=args.limit,
                output_path=output,
                delay=args.delay,
                fetch_details=False,
            )
        except SystemExit as exc:
            stopped_by_limit = True
            print(f"stop_reason crawler_exit={exc.code} batch={batch_name}")
            break
        added, total, skipped_duplicate, skipped_bad = merge_batch(raw_path, output)
        row = {
            "batch": batch_name,
            "crawled": crawled,
            "added": added,
            "total": total,
            "skipped_duplicate": skipped_duplicate,
            "skipped_bad": skipped_bad,
        }
        summary.append(row)
        print("batch_result " + json.dumps(row, ensure_ascii=False))
        ran_batches += 1
        zero_streak = zero_streak + 1 if added == 0 else 0
        if zero_streak >= args.stop_after_zero:
            print(f"stop_reason consecutive_zero_batches={zero_streak}")
            break

    cleaned = clean_file(raw_path, clean_path)
    indexed = build_index(clean_path, Path(args.store))
    print(f"cleaned {cleaned} jobs")
    print(f"indexed {indexed} jobs")
    print(f"stopped_by_limit {stopped_by_limit}")
    print("summary " + json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
