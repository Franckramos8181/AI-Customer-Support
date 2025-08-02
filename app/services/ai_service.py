from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """Je bent een behulpzame klantenservice medewerker voor een grote e-commerce webwinkel.
Je communiceert altijd in het Nederlands. Je bent beleefd, professioneel en empathisch.

Richtlijnen:
- Begroet de klant altijd vriendelijk met "Beste [naam]" of "Dag [naam]"
- Toon begrip voor hun situatie ("Ik begrijp dat...", "Vervelend om te horen dat...")
- Geef duidelijke en concrete antwoorden
- Verwijs naar het beleid wanneer relevant
- Sluit af met een vriendelijke afsluiting ("Met vriendelijke groet", "Hartelijke groet")
- Gebruik een professionele maar warme toon
- Gebruik "u" in plaats van "je" voor formele communicatie
- Vermijd Engelse termen waar Nederlandse alternatieven beschikbaar zijn
- Gebruik Nederlandse datumnotatie (dd-mm-jjjj) en euroteken (€)

Als je context uit de kennisbank krijgt, gebruik die informatie om nauwkeurige antwoorden te geven.
Verzin geen informatie die niet in de context staat.
Verwijs de klant naar de klantenservice als je het antwoord niet weet."""

CATEGORIZE_PROMPT = """Analyseer het volgende klantbericht en categoriseer het.
Geef een JSON-object terug met:
- "categorie": een van ["bestelling", "retour", "betaling", "product", "verzending", "klacht", "overig"]
- "urgentie": een van ["laag", "normaal", "hoog", "kritiek"]
- "samenvatting": een korte samenvatting van het probleem in 1 zin

Klantbericht: {message}"""


def generate_draft_reply(
    customer_message: str,
    conversation_history: list[dict] | None = None,
    knowledge_context: str | None = None,
) -> dict:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if knowledge_context:
        messages.append({
            "role": "system",
            "content": f"Relevante informatie uit de kennisbank:\n\n{knowledge_context}",
        })

    if conversation_history:
        for msg in conversation_history:
            role = "user" if msg["sender_type"] == "customer" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
    else:
        messages.append({"role": "user", "content": customer_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
    )

    reply_content = response.choices[0].message.content
    confidence = _estimate_confidence(reply_content, knowledge_context)

    return {
        "content": reply_content,
        "confidence_score": confidence,
        "model": "gpt-4o-mini",
        "tokens_used": response.usage.total_tokens if response.usage else 0,
    }


def categorize_message(message: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Je bent een classificatiesysteem. Antwoord alleen met JSON."},
            {"role": "user", "content": CATEGORIZE_PROMPT.format(message=message)},
        ],
        temperature=0.3,
        max_tokens=200,
    )

    import json
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"categorie": "overig", "urgentie": "normaal", "samenvatting": message[:100]}


def _estimate_confidence(reply: str, context: str | None) -> int:
    score = 60
    if context:
        score += 25
    if len(reply) > 50:
        score += 10
    if any(word in reply.lower() for word in ["helaas", "sorry", "excuses"]):
        score += 5
    return min(score, 100)
