from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
import os

load_dotenv()

app = FastAPI()

# ================= Supabase =================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= Request Model =================
class Answer(BaseModel):
    current_node: str
    selected_option: str

# ================= Decision Tree =================
decision_tree = {
    "start": {
        "question": "اختر نوع المشكلة:",
        "options": [
            "اختراق حساب",
            "ابتزاز إلكتروني",
            "تهديد إلكتروني",
            "احتيال مالي",
            "سرقة بيانات",
            "انتحال شخصية",
            "أخرى"
        ],
        "next": {
            "اختراق حساب": "hack_q1",
            "ابتزاز إلكتروني": "blackmail_q1",
            "تهديد إلكتروني": "threat_q1",
            "احتيال مالي": "fraud_q1",
            "سرقة بيانات": "data_q1",
            "انتحال شخصية": "impersonation_q1",
            "أخرى": "other_result"
        }
    },

    # ================= ابتزاز =================
    "blackmail_q1": {
        "question": "هل الابتزاز يتضمن:",
        "options": [
            "نشر صور أو ملفات خاصة",
            "طلب مبلغ مالي",
            "تهديد مباشر",
            "أكثر من خيار"
        ],
        "next": {
            "نشر صور أو ملفات خاصة": "blackmail_q2",
            "طلب مبلغ مالي": "blackmail_q2",
            "تهديد مباشر": "blackmail_q2",
            "أكثر من خيار": "blackmail_q2"
        }
    },

    "blackmail_q2": {
        "question": "هل تم التواصل معك عبر الإنترنت؟",
        "options": ["نعم", "لا"],
        "next": {
            "نعم": "blackmail_q3",
            "لا": "blackmail_q3"
        }
    },

    "blackmail_q3": {
        "question": "ما الهدف من التهديد؟",
        "options": [
            "الحصول على المال",
            "التشهير",
            "الضغط والسيطرة",
            "غير واضح"
        ],
        "next": {
            "الحصول على المال": "blackmail_result",
            "التشهير": "blackmail_result",
            "الضغط والسيطرة": "blackmail_result",
            "غير واضح": "blackmail_result"
        }
    },

    "blackmail_result": {
        "label": "ابتزاز إلكتروني"
    },

    # ================= اختراق حساب =================
    "hack_q1": {
        "question": "ما الذي حدث للحساب؟",
        "options": [
            "تم تغيير كلمة المرور",
            "تم تسجيل دخول غريب",
            "فقدت الوصول للحساب"
        ],
        "next": {
            "تم تغيير كلمة المرور": "hack_result",
            "تم تسجيل دخول غريب": "hack_result",
            "فقدت الوصول للحساب": "hack_result"
        }
    },

    "hack_result": {
        "label": "اختراق حساب"
    },

    # ================= تهديد =================
    "threat_q1": {
        "question": "نوع التهديد:",
        "options": [
            "تهديد مباشر",
            "تهديد غير مباشر",
            "تهديد عبر الإنترنت"
        ],
        "next": {
            "تهديد مباشر": "threat_result",
            "تهديد غير مباشر": "threat_result",
            "تهديد عبر الإنترنت": "threat_result"
        }
    },

    "threat_result": {
        "label": "تهديد إلكتروني"
    },

    # ================= احتيال =================
    "fraud_q1": {
        "question": "هل تم تحويل مبلغ مالي؟",
        "options": ["نعم", "لا"],
        "next": {
            "نعم": "fraud_result",
            "لا": "fraud_result"
        }
    },

    "fraud_result": {
        "label": "احتيال مالي"
    },

    # ================= سرقة بيانات =================
    "data_q1": {
        "question": "ما نوع البيانات المسروقة؟",
        "options": [
            "بيانات شخصية",
            "حسابات",
            "معلومات حساسة"
        ],
        "next": {
            "بيانات شخصية": "data_result",
            "حسابات": "data_result",
            "معلومات حساسة": "data_result"
        }
    },

    "data_result": {
        "label": "سرقة بيانات"
    },

    # ================= انتحال شخصية =================
    "impersonation_q1": {
        "question": "هل يوجد حساب ينتحل شخصيتك؟",
        "options": ["نعم", "لا"],
        "next": {
            "نعم": "impersonation_result",
            "لا": "impersonation_result"
        }
    },

    "impersonation_result": {
        "label": "انتحال شخصية"
    },

    # ================= أخرى =================
    "other_result": {
        "message": "لم يتم تحديد نوع دقيق للحالة — يرجى استخدام الإدخال الحر."
    }
}

# ================= Mapping between app labels and DB names =================
# بعض أسماء الجرائم في التطبيق مختصرة، بينما أسماء قاعدة البيانات أطول.
# نحط احتمالات متعددة عشان البحث يكون مرن.
LABEL_TO_CATEGORY_NAMES = {
    "ابتزاز إلكتروني": [
        "ابتزاز إلكتروني",
        "نشر بيانات أو صور سرية بهدف الابتزاز",
        "نشر الصور أو المقاطع الخاصة بدون إذن"
    ],
    "اختراق حساب": [
        "اختراق حساب",
        "دخول غير مشروع / اختراق حسابات",
        "اختراق الأنظمة أو المواقع",
        "تعطيل الخدمات أو إعاقة الوصول للأنظمة"
    ],
    "تهديد إلكتروني": [
        "تهديد إلكتروني",
        "تهديد إلكتروني",
        "تحرش إلكتروني"
    ],
    "احتيال مالي": [
        "احتيال مالي",
        "احتيال مالي إلكتروني",
        "سرقة البيانات البنكية أو بطاقات الدفع"
    ],
    "سرقة بيانات": [
        "سرقة بيانات",
        "إتلاف البيانات أو حذفها أو تعديلها",
        "انتهاك الخصوصية"
    ],
    "انتحال شخصية": [
        "انتحال شخصية",
        "انتحال الهوية الرقمية",
        "إنشاء أو استخدام حسابات مزيفة"
    ]
}

# ================= Supabase Helpers =================
def safe_table_select(table_name: str):
    if not supabase:
        return None
    return supabase.table(table_name)

def get_crime_category_by_label(label: str):
    """
    يحاول يجيب الجريمة من جدول crime_categories
    باستخدام أكثر من اسم محتمل.
    """
    if not supabase:
        return None

    possible_names = LABEL_TO_CATEGORY_NAMES.get(label, [label])

    for name in possible_names:
        try:
            response = (
                supabase.table("crime_categories")
                .select("*")
                .eq("name", name)
                .limit(1)
                .execute()
            )
            if response.data:
                return response.data[0]
        except Exception:
            pass

    return None

def get_legal_articles_for_category(category_id: int):
    """
    يجيب المواد القانونية المرتبطة بالجريمة عبر جدول الربط legal_article_categories
    """
    if not supabase:
        return []

    try:
        link_response = (
            supabase.table("legal_article_categories")
            .select("legal_article_id")
            .eq("crime_category_id", category_id)
            .execute()
        )

        article_ids = [row["legal_article_id"] for row in link_response.data if row.get("legal_article_id") is not None]

        if not article_ids:
            return []

        articles_response = (
            supabase.table("legal_articles")
            .select("id, article_number, article_title, article_content, penalty_details, reference_url")
            .in_("id", article_ids)
            .execute()
        )

        return articles_response.data or []

    except Exception:
        return []

def get_reporting_methods_for_category(category_id: int):
    """
    يجيب طرق التبليغ المرتبطة بالجريمة عبر جدول الربط reporting_method_categories
    """
    if not supabase:
        return []

    try:
        link_response = (
            supabase.table("reporting_method_categories")
            .select("reporting_method_id")
            .eq("crime_category_id", category_id)
            .execute()
        )

        method_ids = [row["reporting_method_id"] for row in link_response.data if row.get("reporting_method_id") is not None]

        if not method_ids:
            return []

        methods_response = (
            supabase.table("reporting_methods")
            .select("id, method_name, authority_name, channel_type, description")
            .in_("id", method_ids)
            .execute()
        )

        return methods_response.data or []

    except Exception:
        return []

def format_result_message(label: str) -> str:
    """
    يبني رسالة نهائية واحدة تُعرض مباشرة في نفس شاشة Guided Selection
    بدون الحاجة لتعديل الواجهة.
    """
    base_message = f"بعد تحليل إجاباتك، تم تصنيف الحالة كالتالي:\n{label}"

    if not supabase:
        return base_message + "\n\nتعذر جلب البيانات المرتبطة لأن الاتصال بقاعدة البيانات غير متاح."

    category = get_crime_category_by_label(label)

    if not category:
        return base_message + "\n\nلم يتم العثور على بيانات مرتبطة بهذه الجريمة في قاعدة البيانات."

    category_id = category.get("id")
    category_description = category.get("description", "")

    articles = get_legal_articles_for_category(category_id)
    reporting_methods = get_reporting_methods_for_category(category_id)

    parts = [base_message]

    if category_description:
        parts.append(f"\nالوصف:\n{category_description}")

    if articles:
        article_texts = []
        for article in articles[:3]:
            article_number = article.get("article_number") or "بدون رقم"
            article_title = article.get("article_title") or "بدون عنوان"
            article_content = article.get("article_content") or "لا يوجد نص"
            penalty_details = article.get("penalty_details") or "لا توجد تفاصيل عقوبة"

            article_texts.append(
                f"• {article_number} - {article_title}\n"
                f"النص: {article_content}\n"
                f"العقوبة: {penalty_details}"
            )

        parts.append("\nالمادة القانونية والعقوبة:\n" + "\n\n".join(article_texts))
    else:
        parts.append("\nالمادة القانونية والعقوبة:\nلا توجد مادة قانونية مرتبطة حاليًا.")

    if reporting_methods:
        reporting_texts = []
        for method in reporting_methods[:5]:
            method_name = method.get("method_name") or "طريقة تبليغ"
            authority_name = method.get("authority_name") or "جهة غير محددة"
            channel_type = method.get("channel_type") or "غير محدد"
            description = method.get("description") or ""

            text = f"• {method_name} - {authority_name} ({channel_type})"
            if description:
                text += f"\n{description}"
            reporting_texts.append(text)

        parts.append("\nخطوات التبليغ:\n" + "\n\n".join(reporting_texts))
    else:
        parts.append("\nخطوات التبليغ:\nلا توجد طرق تبليغ مرتبطة حاليًا.")

    return "\n".join(parts)

# ================= API =================
@app.get("/start")
def start():
    return {
        "node_id": "start",
        **decision_tree["start"]
    }

@app.post("/next")
def next_step(answer: Answer):
    node = decision_tree.get(answer.current_node)

    if not node:
        return {"error": "node not found"}

    next_node_key = node.get("next", {}).get(answer.selected_option)

    if not next_node_key:
        return {"error": "invalid option"}

    next_node = decision_tree[next_node_key]

    if "label" in next_node:
        label = next_node["label"]
        final_message = format_result_message(label)

        return {
            "node_id": next_node_key,
            "message": final_message
        }

    if "message" in next_node:
        return {
            "node_id": next_node_key,
            "message": next_node["message"]
        }

    return {
        "node_id": next_node_key,
        **next_node
    }