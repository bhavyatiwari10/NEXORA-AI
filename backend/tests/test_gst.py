from app.services.gst import gst_breakup
def test_intra_state_gst():
    x=gst_breakup(1000,18,'Uttar Pradesh','Uttar Pradesh'); assert x['cgst']==90 and x['sgst']==90 and x['igst']==0 and x['total']==1180
def test_inter_state_gst():
    x=gst_breakup(1000,18,'Uttar Pradesh','Delhi'); assert x['igst']==180 and x['cgst']==0
