"""Seed the database with sample conversations for demo purposes."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import Conversation, Message, DraftReply, ConversationStatus, DraftStatus

SAMPLE_CONVERSATIONS = [
    {
        "customer_name": "Jan de Vries",
        "customer_email": "jan.devries@email.nl",
        "subject": "Bestelling niet ontvangen - Order #12847",
        "status": ConversationStatus.OPEN,
        "messages": [
            {
                "sender_type": "customer",
                "content": "Goedemiddag,\n\nIk heb op 15 september een bestelling geplaatst (ordernummer #12847) maar ik heb deze nog steeds niet ontvangen. Volgens de track & trace code zou het pakket op 18 september bezorgd zijn, maar ik was die dag thuis en er is niemand langs geweest.\n\nKunt u mij helpen met het opsporen van mijn pakket?\n\nMet vriendelijke groet,\nJan de Vries",
            },
        ],
    },
    {
        "customer_name": "Maria Jansen",
        "customer_email": "m.jansen@outlook.nl",
        "subject": "Retour aanvragen - Verkeerde maat ontvangen",
        "status": ConversationStatus.IN_PROGRESS,
        "messages": [
            {
                "sender_type": "customer",
                "content": "Hallo,\n\nIk heb vorige week een winterjas besteld in maat L, maar ik heb maat XL ontvangen. Ik wil graag de juiste maat ontvangen. Hoe kan ik dit product retourneren en de juiste maat bestellen?\n\nAlvast bedankt,\nMaria Jansen",
            },
            {
                "sender_type": "agent",
                "content": "Beste Maria,\n\nVervelend om te horen dat u de verkeerde maat heeft ontvangen. Ik help u graag met de retour.\n\nU kunt de jas retourneren via uw account. Ik heb alvast een retourlabel voor u aangemaakt dat u per e-mail ontvangt. De retour is uiteraard kosteloos aangezien het om een fout van onze kant gaat.\n\nZodra wij de jas retour hebben ontvangen, sturen wij direct de juiste maat (L) naar u op.\n\nMet vriendelijke groet,\nKlantenservice",
            },
            {
                "sender_type": "customer",
                "content": "Dank u wel voor de snelle reactie! Ik heb het retourlabel ontvangen. Ik lever het pakket morgen in bij het PostNL punt. Hoe lang duurt het voordat ik de juiste maat ontvang?\n\nGroetjes,\nMaria",
            },
        ],
        "draft": {
            "content": "Beste Maria,\n\nFijn om te horen dat u het retourlabel heeft ontvangen! Zodra wij uw retour hebben ontvangen en gecontroleerd, wordt de winterjas in maat L direct naar u verzonden. Normaal gesproken duurt dit 1-3 werkdagen na ontvangst van de retour.\n\nU kunt de status volgen via uw account. Mocht u nog vragen hebben, dan hoor ik het graag.\n\nMet vriendelijke groet,\nKlantenservice",
            "confidence_score": 87,
            "status": DraftStatus.PENDING,
        },
    },
    {
        "customer_name": "Peter van den Berg",
        "customer_email": "p.vandenberg@gmail.com",
        "subject": "Klacht over beschadigd product",
        "status": ConversationStatus.OPEN,
        "messages": [
            {
                "sender_type": "customer",
                "content": "Geachte klantenservice,\n\nVandaag heb ik mijn bestelling ontvangen maar helaas is het product (een glazen vaas, artikelnummer VAZ-2847) beschadigd aangekomen. De vaas heeft een scheur aan de zijkant en is onbruikbaar.\n\nIk heb foto's gemaakt van de schade en de verpakking. Hoe kan ik deze naar jullie sturen? Ik wil graag een vervanging of mijn geld terug.\n\nMet vriendelijke groet,\nPeter van den Berg",
            },
        ],
    },
    {
        "customer_name": "Sophie Bakker",
        "customer_email": "sophie.b@hotmail.nl",
        "subject": "Vraag over verzendkosten naar België",
        "status": ConversationStatus.RESOLVED,
        "messages": [
            {
                "sender_type": "customer",
                "content": "Hoi,\n\nIk woon in België en wil graag een bestelling plaatsen. Wat zijn de verzendkosten naar België? En is er een minimumbedrag voor gratis verzending?\n\nGroetjes,\nSophie",
            },
            {
                "sender_type": "agent",
                "content": "Beste Sophie,\n\nBedankt voor uw interesse in onze webshop! De verzendkosten naar België zijn als volgt:\n\n- Standaard verzending: €6,95 (levertijd 2-4 werkdagen)\n- Express verzending: €9,95 (levertijd 1-2 werkdagen)\n- Gratis verzending bij bestellingen boven €75\n\nWij werken voor leveringen naar België samen met bpost, zodat u uw pakket gemakkelijk kunt volgen.\n\nMocht u nog vragen hebben, dan help ik u graag verder!\n\nMet vriendelijke groet,\nKlantenservice",
            },
        ],
    },
    {
        "customer_name": "Thomas Willems",
        "customer_email": "t.willems@kpn.nl",
        "subject": "Achteraf betalen via Klarna werkt niet",
        "status": ConversationStatus.OPEN,
        "messages": [
            {
                "sender_type": "customer",
                "content": "Hallo,\n\nIk probeer een bestelling te plaatsen met Klarna (achteraf betalen), maar bij het afrekenen krijg ik steeds een foutmelding. Ik heb het al meerdere keren geprobeerd met verschillende browsers.\n\nDe foutmelding is: 'Betaling kan niet worden verwerkt. Probeer het later opnieuw.'\n\nKunnen jullie mij helpen? Ik wil graag mijn bestelling afronden.\n\nGroeten,\nThomas Willems",
            },
        ],
    },
]


def seed():
    init_db()
    db = SessionLocal()

    existing = db.query(Conversation).count()
    if existing > 0:
        print(f"Database bevat al {existing} gesprekken. Overslaan...")
        db.close()
        return

    print("Voorbeeldgesprekken laden...")

    for conv_data in SAMPLE_CONVERSATIONS:
        conversation = Conversation(
            customer_name=conv_data["customer_name"],
            customer_email=conv_data["customer_email"],
            subject=conv_data["subject"],
            status=conv_data["status"],
        )
        db.add(conversation)
        db.flush()

        for msg_data in conv_data["messages"]:
            message = Message(
                conversation_id=conversation.id,
                sender_type=msg_data["sender_type"],
                content=msg_data["content"],
            )
            db.add(message)

        if "draft" in conv_data:
            draft = DraftReply(
                conversation_id=conversation.id,
                content=conv_data["draft"]["content"],
                confidence_score=conv_data["draft"]["confidence_score"],
                status=conv_data["draft"]["status"],
            )
            db.add(draft)

        print(f"  + {conv_data['subject']}")

    db.commit()
    db.close()

    print(f"\nKlaar! {len(SAMPLE_CONVERSATIONS)} voorbeeldgesprekken geladen.")


if __name__ == "__main__":
    seed()
