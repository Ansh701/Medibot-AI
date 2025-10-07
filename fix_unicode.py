import os


def fix_file(filename, fixes):
    """Fix Unicode characters in a file"""
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        original_content = content

        for old_text, new_text in fixes.items():
            content = content.replace(old_text, new_text)

        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✓ Fixed {filename}")
        else:
            print(f"○ No changes needed in {filename}")

    except Exception as e:
        print(f"❌ Error fixing {filename}: {e}")


# Define the fixes needed
fixes = {
    # Helper file fixes
    'src/helper.py': {
        'logger.info("✅ HuggingFace embeddings initialized")': 'logger.info("HuggingFace embeddings initialized successfully")',
        'logger.info(f"✅ Loaded {len(documents)} documents from {data}")': 'logger.info(f"Loaded {len(documents)} documents from {data}")',
        'logger.info(f"✅ Filtered {len(minimal_docs)} documents")': 'logger.info(f"Filtered {len(minimal_docs)} documents")',
        'logger.info(f"✅ Created {len(text_chunks)} text chunks")': 'logger.info(f"Created {len(text_chunks)} text chunks")',
    },

    # Medical RAG fixes
    'src/medical_rag.py': {
        'logger.info(f"✅ Connected to Pinecone index: {index_name}")': 'logger.info(f"Connected to Pinecone index: {index_name}")',
    },

    # App fixes
    'app.py': {
        'logger.info("✅ Advanced Medical RAG System initialized")': 'logger.info("Advanced Medical RAG System initialized successfully")',
        '🏥 Initializing Advanced Medical RAG System...': 'Initializing Advanced Medical RAG System...',
    },

    # LLM Handler fixes
    'src/llm_handler.py': {
        'logger.info("✅ Gemini initialized")': 'logger.info("Gemini initialized successfully")',
        'logger.info("✅ OpenAI initialized")': 'logger.info("OpenAI initialized successfully")',
        'logger.info("✅ Anthropic initialized")': 'logger.info("Anthropic initialized successfully")',
        'logger.info(f"📡 Initialized {len(llm_providers)} LLM provider(s)")': 'logger.info(f"Initialized {len(llm_providers)} LLM provider(s)")',
        'logger.warning("⚠️ Using dummy LLM - please configure API keys")': 'logger.warning("Using dummy LLM - please configure API keys")',
        'logger.error("❌ No LLM providers could be initialized. Please check your API keys in the .env file.")': 'logger.error("No LLM providers could be initialized. Please check your API keys in the .env file.")',
        'logger.warning(f"⚠️ Could not initialize Gemini: {e}")': 'logger.warning(f"Could not initialize Gemini: {e}")',
        'logger.warning(f"⚠️ Could not initialize OpenAI: {e}")': 'logger.warning(f"Could not initialize OpenAI: {e}")',
        'logger.warning(f"⚠️ Could not initialize Anthropic: {e}")': 'logger.warning(f"Could not initialize Anthropic: {e}")',
    }
}

print("🔧 Fixing Unicode characters in MediBot files...")
print("=" * 50)

for filename, file_fixes in fixes.items():
    fix_file(filename, file_fixes)

print("=" * 50)
print("✅ All files processed! Run 'python app.py' now.")
