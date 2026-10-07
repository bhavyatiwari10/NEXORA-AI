from app.llm.mock import MockLLM
def test_mock_extracts_order():
    x=MockLLM().extract('bhai 2 kg basmati rice chahiye, kal tak deliver ho jayega?')
    assert x.intent.value=='order' and x.products[0].quantity==2 and x.language=='Hinglish'
