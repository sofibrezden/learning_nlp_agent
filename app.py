import json
import os
from pathlib import Path

import streamlit as st
from openai import OpenAI

from tools import iso_now, tool_router

TOOLS = json.loads(Path("data/tools.json").read_text(encoding="utf-8"))
SYSTEM_INSTRUCTIONS = Path("prompt.txt").read_text(encoding="utf-8").strip()


def init_session_state() -> None:
    """Initialize all required session_state keys."""
    st.session_state.setdefault("chat_display", [])
    st.session_state.setdefault("openai_input", [])
    st.session_state.setdefault("audit_history", [])
    st.session_state.setdefault("exam", None)
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("last_result_blob", None)


def reset_session() -> None:
    """Hard reset Streamlit session."""
    for key in [
        "chat_display",
        "openai_input",
        "audit_history",
        "exam",
        "last_result",
        "last_result_blob",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


def audit_log(role: str, content: str) -> None:
    if "audit_history" not in st.session_state:
        st.session_state.audit_history = []

    st.session_state.audit_history.append(
        {
            "role": role,
            "content": content,
            "datetime": iso_now(),
        }
    )


def add_message(role: str, content: str) -> None:
    """Add message to UI + audit log."""
    st.session_state.chat_display.append({"role": role, "content": content})
    audit_log(role if role != "assistant" else "system", content)


def run_agent_turn(client: OpenAI, model: str, user_text: str) -> str:
    st.session_state.openai_input.append({"role": "user", "content": user_text})

    with st.spinner("Думаю..."):
        while True:
            response = client.responses.create(
                model=model,
                instructions=SYSTEM_INSTRUCTIONS,
                tools=TOOLS,
                input=st.session_state.openai_input,
                temperature=0.0,
            )

            for item in response.output:
                if hasattr(item, "model_dump"):
                    st.session_state.openai_input.append(item.model_dump())
                else:
                    st.session_state.openai_input.append(item)

            tool_calls = [
                item for item in response.output if getattr(item, "type", None) == "function_call"
            ]

            if not tool_calls:
                return response.output_text

            for call in tool_calls:
                tool_name = call.name
                tool_args = json.loads(call.arguments or "{}")
                if tool_name == "end_exam":
                    tool_output = tool_router(
                        tool_name,
                        {**tool_args, "history": st.session_state.get("audit_history", [])},
                    )
                else:
                    tool_output = tool_router(tool_name, tool_args)

                audit_log(
                    "tool_call",
                    f"{tool_name} args={tool_args} output={tool_output}",
                )
                st.session_state.openai_input.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(tool_output, ensure_ascii=False),
                    }
                )


def render_sidebar() -> tuple[str, str]:
    with st.sidebar:
        st.header("⚙️ Налаштування")
        api_key = st.text_input(
            "OpenAI API key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
        )
        model = st.text_input("Model", value="gpt-4.1")
        st.caption(
            "🧠 Введіть назву моделі, яку підтримує ваш OpenAI API ключ (наприклад, `gpt-4.1`)."
        )
        st.caption("🔒 Ключ зберігається тільки в сесії браузера.")

        if st.button("🔄 Reset session"):
            reset_session()

    return api_key, model


def render_chat() -> None:
    for msg in st.session_state.chat_display:
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(msg["content"])


def render_greeting() -> None:
    if not st.session_state.chat_display:
        greet = (
            "Привіт! Я екзаменатор з NLP. "
            "Скажи, будь ласка, своє **імʼя** та **email** "
            "і ми почнемо."
        )
        add_message("assistant", greet)


def main() -> None:
    st.set_page_config(
        page_title="AI Examiner Agent (NLP)",
        page_icon="🧠",
        layout="wide",
    )
    init_session_state()

    st.title("🧠 AI Examiner Agent — NLP Exam Demo")
    st.write(
        "Екзаменатор: збирає імʼя+email, вибирає теми, проводить діалог та зберігає результат."
    )

    api_key, model = render_sidebar()
    render_greeting()
    render_chat()

    if st.session_state.get("last_result"):
        result = st.session_state["last_result"]
        st.success("✅ Іспит завершено")
        st.metric("Ваш результат", f"{float(result['score']):.2f}")
        st.download_button(
            label="⬇️ Завантажити мій результат",
            data=st.session_state["last_result_blob"] or "",
            file_name="exam_result.json",
            mime="application/json",
        )
        st.stop()

    user_input = st.chat_input("Відповідь…")
    if user_input:
        if not api_key:
            st.error("Додай API key у сайдбарі.")
            st.stop()

        client = OpenAI(api_key=api_key)
        add_message("user", user_input)
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("⏳ Думаю...")

            assistant_text = run_agent_turn(
                client=client,
                model=model,
                user_text=user_input,
            )
            add_message("assistant", assistant_text)
            message_placeholder.markdown(assistant_text)

        st.rerun()


if __name__ == "__main__":
    main()
