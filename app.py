import gradio as gr
from sidekick import Sidekick


async def setup():
    sidekick = Sidekick()
    await sidekick.setup()
    return sidekick

async def process_message(sidekick, message, success_criteria, history):
    results = await sidekick.run_superstep(message, success_criteria, history)
    
    # Check if any files were created in the sandbox directory
    import os
    import glob
    from pathlib import Path
    
    # Look for PDF files in the sandbox directory
    sandbox_path = Path("sandbox")
    pdf_files = list(sandbox_path.glob("*.pdf"))
    
    # Return the most recent PDF file if any exist
    file_output = None
    if pdf_files:
        # Get the most recent PDF file
        latest_pdf = max(pdf_files, key=os.path.getctime)
        file_output = str(latest_pdf)
    
    return results, sidekick, file_output
    
async def reset():
    new_sidekick = Sidekick()
    await new_sidekick.setup()
    return "", "", None, new_sidekick, None

def free_resources(sidekick):
    print("Cleaning up")
    try:
        if sidekick:
            sidekick.free_resources()
    except Exception as e:
        print(f"Exception during cleanup: {e}")


with gr.Blocks(title="Sidekick", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## Sidekick Personal Co-Worker")
    sidekick = gr.State(delete_callback=free_resources)
    
    with gr.Row():
        chatbot = gr.Chatbot(label="Sidekick", height=300, type="messages")
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to the Sidekick")
        with gr.Row():
            success_criteria = gr.Textbox(show_label=False, placeholder="What are your success critiera?")
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go!", variant="primary")
    
    # File download component for PDFs and other files
    with gr.Row():
        file_output = gr.File(label="Download Generated Files", visible=False)
        
    ui.load(setup, [], [sidekick])
    message.submit(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick, file_output])
    success_criteria.submit(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick, file_output])
    go_button.click(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick, file_output])
    reset_button.click(reset, [], [message, success_criteria, chatbot, sidekick, file_output])

    
ui.launch(inbrowser=True)