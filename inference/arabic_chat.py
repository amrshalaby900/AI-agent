import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer

def start_arabic_chat():
    # 1. تحميل النموذج المطور (أو النموذج الأساسي)
    model_path = "arabic_model_final" # أو مسار النموذج الذي قمت بتطويره
    print(f"جاري تحميل النموذج العربي من: {model_path}...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype = torch.float16,
            device_map = "auto",
        )
    except:
        print("تنبيه: لم يتم العثور على نموذج مطور، جاري تحميل النموذج الأساسي للتجربة...")
        model_path = "unsloth/DeepSeek-R1-Distill-Qwen-7B"
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype = torch.float16,
            device_map = "auto",
        )

    # 2. إعداد المحادثة
    print("\n--- مرحباً بك في واجهة المحادثة العربية الذكية ---")
    print("اكتب 'خروج' لإنهاء المحادثة.\n")
    
    while True:
        user_input = input("أنت: ")
        if user_input.lower() in ["خروج", "exit", "quit"]:
            break
            
        # تنسيق المدخلات للغة العربية
        prompt = f"### تعليمات:\nأجب على السؤال التالي باللغة العربية الفصحى وبشكل مفصل.\n\n### سؤال:\n{user_input}\n\n### استجابة:\n"
        
        inputs = tokenizer([prompt], return_tensors = "pt").to("cuda")
        
        # استخدام Streamer لرؤية الإجابة وهي تُكتب أمامك
        text_streamer = TextStreamer(tokenizer)
        
        print("الذكاء الاصطناعي العربي: ", end="")
        _ = model.generate(
            **inputs, 
            streamer = text_streamer, 
            max_new_tokens = 512,
            temperature = 0.7,
            top_p = 0.9,
        )
        print("\n")

if __name__ == "__main__":
    start_arabic_chat()
