from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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
        "message": "بعد تحليل إجاباتك، تم تصنيف الحالة كالتالي:\nابتزاز إلكتروني — يتضمن تهديد أو ضغط باستخدام معلومات أو محتوى شخصي."
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
        "message": "تم تصنيف الحالة:\nاختراق حساب — دخول غير مصرح به أو فقدان السيطرة على الحساب."
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
        "message": "تم تصنيف الحالة:\nتهديد إلكتروني — وجود تهديد أو تخويف عبر وسيلة رقمية."
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
        "message": "تم تصنيف الحالة:\nاحتيال مالي — محاولة أو عملية خداع للحصول على أموال."
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
        "message": "تم تصنيف الحالة:\nسرقة بيانات — الوصول غير المصرح به إلى معلومات شخصية أو حساسة."
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
        "message": "تم تصنيف الحالة:\nانتحال شخصية — استخدام اسم أو بيانات شخص آخر بدون إذن."
    },

    # ================= أخرى =================
    "other_result": {
        "message": "لم يتم تحديد نوع دقيق للحالة — يرجى استخدام الإدخال الحر."
    }
}

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

    if "message" in next_node:
        return {
            "node_id": next_node_key,
            "message": next_node["message"]
        }

    return {
        "node_id": next_node_key,
        **next_node
    }