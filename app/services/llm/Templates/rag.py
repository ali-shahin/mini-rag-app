from string import Template

system_promt = Template("\n".join([
    "You are a helpful assistant.",
    "You are an expert in the domain of $domain.",
    "be clear and concise in your answers.",
    "If you don't know the answer, just say that you don't know. Don't try to make up an answer.",

]))

document_prompt = Template("\n".join([
    "## Document: $document_name",
    "### Content: $content",
]))

footer_prompt = Template("\n".join([
    "based on the above documents only, generate an answer to the question:",
    "### Question: $question",
    "\n\n",
    "## Answer:",
]))

def get_system_prompt(domain):
    return system_promt.substitute(domain=domain)

def get_document_prompt(document_name, content):
    return document_prompt.substitute(document_name=document_name, content=content)

def get_footer_prompt(question):
    return footer_prompt