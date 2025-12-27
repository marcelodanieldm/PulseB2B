from typing import Dict

class TelegramTeaserGenerator:
    def generate_teaser(self, company: Dict) -> str:
        # Placeholder: implement real summarization logic
        return f"🏢 {company.get('name', 'Company')}\n💰 Funding: {company.get('total_funding', 'N/A')}\n🔥 Hiring Probability: {company.get('hiring_probability', 'N/A')}%"
