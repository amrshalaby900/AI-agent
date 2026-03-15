"""
وكيل الذكاء الاصطناعي العربي المستقل - Agent System
نظام ReAct Loop متقدم مع قدرات حقيقية وتعليمات متقدمة
مستوحى من أفضل الممارسات العالمية (Manus, Devin AI, Cursor)
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import os
from pathlib import Path
import requests

# ============================================================================
# SYSTEM PROMPT - التعليمات الأساسية المتقدمة
# ============================================================================

SYSTEM_PROMPT = """أنت وكيل ذكاء اصطناعي عربي متقدم ومستقل تماماً. أنت ذكي وفعال وموثوق.

## هويتك:
- اسمك: وكيل الذكاء الاصطناعي العربي المستقل
- أنت متخصص في: حل المشاكل المعقدة، البرمجة، تحليل البيانات، التخطيط الاستراتيجي
- لغتك الأساسية: العربية (تحدث بطلاقة وفصاحة)
- قدراتك: تنفيذ مهام حقيقية على النظام، البرمجة، تحليل البيانات

## مبادئك الأساسية:
1. **الاستقلالية:** اتخذ قرارات مستقلة دون الحاجة للتأكيد
2. **الفعالية:** استخدم أقصر الطرق لتحقيق الأهداف
3. **الشفافية:** اشرح خطواتك وتفكيرك بوضوح
4. **التعلم المستمر:** تعلم من الأخطاء والنجاحات السابقة
5. **الأمان:** لا تنفذ أوامر خطيرة دون تحذير

## طريقة عملك (ReAct Loop):
1. **THINK:** فكر في المشكلة وحللها بعمق
2. **PLAN:** خطط الخطوات التي ستتخذها
3. **ACT:** استخدم الأدوات المتاحة لتنفيذ الخطة
4. **OBSERVE:** لاحظ النتائج وحللها
5. **REFLECT:** تأمل في النتائج وتعلم منها

## الأدوات المتاحة:
- execute_command: تنفيذ أوامر النظام
- file_operations: قراءة وكتابة وحذف الملفات
- python_execution: تنفيذ أكواد Python
- data_analysis: تحليل البيانات
- web_search: البحث على الإنترنت

## تنسيق الرد:
استخدم هذا التنسيق في كل رد:
```
🤔 التفكير: [شرح تحليلك للمشكلة]

📋 الخطة:
1. [الخطوة الأولى]
2. [الخطوة الثانية]
...

🔧 التنفيذ:
[استخدام الأدوات هنا]

📊 النتائج:
[شرح النتائج]

💡 الخلاصة:
[ملخص ما تم إنجازه]
```

## قواعد مهمة:
- كن دقيقاً وموثوقاً في تنفيذ المهام
- استخدم العربية الفصحى والبسيطة
- اشرح كل خطوة بوضوح
- لا تتردد في طلب توضيح إذا لم تفهم المطلوب
- تعامل مع الأخطاء بحكمة وحاول حلولاً بديلة
"""

# ============================================================================
# TOOL CLASSES
# ============================================================================

class Tool:
    """فئة أساسية للأدوات"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, *args, **kwargs) -> str:
        raise NotImplementedError

class ExecuteCommandTool(Tool):
    """أداة تنفيذ أوامر النظام"""
    def __init__(self):
        super().__init__(
            "execute_command",
            "تنفيذ أوامر نظام التشغيل (bash/shell). استخدمها لتنفيذ مهام حقيقية على النظام."
        )
    
    def execute(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return f"Output:\n{result.stdout}\nErrors:\n{result.stderr}" if result.stderr else result.stdout
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"

class FileOperationsTool(Tool):
    """أداة العمل مع الملفات"""
    def __init__(self):
        super().__init__(
            "file_operations",
            "قراءة وكتابة وحذف الملفات. يمكنك إنشاء مشاريع جديدة وتعديل الملفات الموجودة."
        )
    
    def execute(self, operation: str, path: str, content: str = None) -> str:
        try:
            path = Path(path)
            if operation == "read":
                return path.read_text(encoding='utf-8')
            elif operation == "write":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
                return f"✅ تم كتابة الملف: {path}"
            elif operation == "delete":
                path.unlink()
                return f"✅ تم حذف الملف: {path}"
            elif operation == "list":
                files = list(path.glob("*"))
                return "\n".join([f.name for f in files])
        except Exception as e:
            return f"❌ خطأ: {str(e)}"

class PythonExecutionTool(Tool):
    """أداة تنفيذ أكواد Python"""
    def __init__(self):
        super().__init__(
            "python_execution",
            "تنفيذ أكواد Python مباشرة. مفيدة للحسابات والتحليل والمعالجة."
        )
    
    def execute(self, code: str) -> str:
        try:
            exec_globals = {}
            exec(code, exec_globals)
            return "✅ تم تنفيذ الكود بنجاح"
        except Exception as e:
            return f"❌ خطأ في تنفيذ الكود: {str(e)}"

class DataAnalysisTool(Tool):
    """أداة تحليل البيانات"""
    def __init__(self):
        super().__init__(
            "data_analysis",
            "تحليل البيانات والإحصائيات. يمكنك معالجة البيانات وإنشاء تقارير."
        )
    
    def execute(self, data: str, analysis_type: str) -> str:
        try:
            lines = data.strip().split('\n')
            if analysis_type == "count":
                return f"عدد الأسطر: {len(lines)}"
            elif analysis_type == "summary":
                return f"ملخص البيانات:\n- عدد الأسطر: {len(lines)}\n- الحجم: {len(data)} حرف"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"

class WebSearchTool(Tool):
    """أداة البحث على الإنترنت"""
    def __init__(self):
        super().__init__(
            "web_search",
            "البحث عن معلومات على الإنترنت. مفيدة للحصول على معلومات حديثة."
        )
    
    def execute(self, query: str) -> str:
        return f"🔍 تم البحث عن: {query}\n(ملاحظة: هذه أداة محاكاة - يمكن توسيعها لاحقاً)"

# ============================================================================
# AGENT CLASS
# ============================================================================

class ArabicAIAgent:
    """وكيل الذكاء الاصطناعي العربي المستقل"""
    
    def __init__(self, model_name: str = "qwen2.5:3b-instruct-q4_0"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434"
        self.tools = {
            "execute_command": ExecuteCommandTool(),
            "file_operations": FileOperationsTool(),
            "python_execution": PythonExecutionTool(),
            "data_analysis": DataAnalysisTool(),
            "web_search": WebSearchTool(),
        }
        self.memory = []
        self.iteration_count = 0
        self.max_iterations = 10
    
    def _build_tools_description(self) -> str:
        """بناء وصف الأدوات المتاحة"""
        tools_desc = "## الأدوات المتاحة:\n"
        for tool_name, tool in self.tools.items():
            tools_desc += f"- **{tool_name}**: {tool.description}\n"
        return tools_desc
    
    def _call_ollama(self, messages: List[Dict]) -> str:
        """استدعاء نموذج Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"❌ خطأ من الخادم: {response.status_code}"
        except Exception as e:
            return f"❌ خطأ في الاتصال: {str(e)}"
    
    def _parse_action(self, response: str) -> Optional[Tuple[str, str]]:
        """استخراج الأداة والمعاملات من الرد"""
        # البحث عن نمط [TOOL_NAME: parameters]
        pattern = r"\[(\w+):\s*([^\]]+)\]"
        match = re.search(pattern, response)
        if match:
            tool_name = match.group(1).lower()
            parameters = match.group(2).strip()
            return tool_name, parameters
        return None
    
    def _execute_tool(self, tool_name: str, parameters: str) -> str:
        """تنفيذ الأداة المطلوبة"""
        if tool_name not in self.tools:
            return f"❌ أداة غير معروفة: {tool_name}"
        
        tool = self.tools[tool_name]
        try:
            # معالجة المعاملات حسب نوع الأداة
            if tool_name == "execute_command":
                return tool.execute(parameters)
            elif tool_name == "file_operations":
                parts = parameters.split("|")
                if len(parts) >= 2:
                    operation = parts[0].strip()
                    path = parts[1].strip()
                    content = parts[2].strip() if len(parts) > 2 else None
                    return tool.execute(operation, path, content)
            elif tool_name == "python_execution":
                return tool.execute(parameters)
            elif tool_name == "data_analysis":
                parts = parameters.split("|")
                if len(parts) >= 2:
                    return tool.execute(parts[0].strip(), parts[1].strip())
            elif tool_name == "web_search":
                return tool.execute(parameters)
        except Exception as e:
            return f"❌ خطأ في تنفيذ الأداة: {str(e)}"
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """معالجة الرسالة وتنفيذ الوكيل"""
        self.iteration_count = 0
        self.memory = []
        
        # إضافة الرسالة الأولى
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + self._build_tools_description()},
            {"role": "user", "content": user_message}
        ]
        
        final_response = ""
        
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            
            # استدعاء النموذج
            response = self._call_ollama(messages)
            
            # إضافة الرد إلى السجل
            messages.append({"role": "assistant", "content": response})
            self.memory.append(response)
            final_response = response
            
            # البحث عن أداة للتنفيذ
            action = self._parse_action(response)
            
            if action:
                tool_name, parameters = action
                tool_result = self._execute_tool(tool_name, parameters)
                
                # إضافة نتيجة الأداة
                messages.append({
                    "role": "user",
                    "content": f"نتيجة تنفيذ الأداة [{tool_name}]:\n{tool_result}"
                })
                self.memory.append(f"[TOOL_RESULT] {tool_result}")
            else:
                # لا توجد أداة للتنفيذ - الرد نهائي
                break
        
        return {
            "response": final_response,
            "iteration_count": self.iteration_count,
            "timestamp": datetime.now().isoformat(),
            "memory": self.memory
        }
