import os

def reassemble_model():
    output_filename = "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf"
    parts = ["model_part_aa", "model_part_ab", "model_part_ac", "model_part_ad", "model_part_ae"]
    
    print(f"جاري تجميع أجزاء النموذج في ملف واحد: {output_filename}...")
    
    try:
        with open(output_filename, 'wb') as output_file:
            for part in parts:
                if os.path.exists(part):
                    print(f"جاري دمج الجزء: {part}")
                    with open(part, 'rb') as part_file:
                        output_file.write(part_file.read())
                else:
                    print(f"خطأ: الجزء {part} غير موجود!")
                    return
        
        print(f"تم التجميع بنجاح! الملف النهائي هو: {output_filename}")
        print("يمكنك الآن حذف الأجزاء (model_part_*) لتوفير المساحة.")
        
    except Exception as e:
        print(f"حدث خطأ أثناء التجميع: {e}")

if __name__ == "__main__":
    reassemble_model()
