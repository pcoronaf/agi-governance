"""
Real-evidence bridgeability study, PRIOR vs CURRENT model generations
(paper Section 8.5). Coverage analysis, NOT auditor-confirmed compliance.

Maps real published model/system cards to the agiev schema and runs the reference
engine to measure which norm inputs are sourceable from real public evidence, and
whether coverage improved from the 2024 generation to the 2025-26 generation.

Mapping discipline (identical across generations): a field/type is present only when
the document provides it (conservative); a separate 'generous proxy' pass adds
documented, FLAGGED proxies from related-but-not-identical metrics. Cross-cutting
meta-fields are assigned from the document so gaps are driven by indicator/artifact
absence. Proxy numeric values are ILLUSTRATIVE (the finding is which CATEGORY of
norm becomes evaluable).

Mapping provenance: the CARDS mapping below is the CONSENSUS of three independent
coders (author team + two external ISO/IEC 42001 auditors; strict-pass unanimity,
generous-pass Fleiss' kappa = 0.709). The four disagreeing cells and their
majority resolution are in reconciliation_log.md; the full judgment matrix is in
coder_agreement_matrix.csv and is reproduced by compute_reliability.py.
Consensus generous-pass positives: IND-ROB-TEST on GPT-4o and Claude 3.5 Sonnet
(2024) and on GPT-5.5, Claude Opus 4.6 and Gemini 3 (2025-26). An earlier
version of this script admitted a risk-category-coverage proxy for IND-ETH-COV
(yielding 3/30 -> 6/30); both external coders rejected it independently (different
denominator concept) and it is not part of the consensus mapping.
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "checker"))
from compliance_engine import run_compliance_check

INDICATORS = {
    "IND-TRANS-AI-ID":("RuntimeTelemetryLog","identity_disclosure_rate"),
    "IND-TRANS-EXP":("ModelCard","explainability_coverage"),
    "IND-CTRL-CEASE-RATE":("RedTeamingReport","cessation_compliance_rate"),
    "IND-CTRL-CEASE-LATENCY":("RuntimeTelemetryLog","mean_time_to_cessation_s"),
    "IND-CTRL-SLO-RATE":("SelfLearningAuditRecord","kae_review_rate"),
    "IND-CTRL-SLO-VIOLATIONS":("SelfLearningAuditRecord","unreviewed_kae_count"),
    "IND-ACC-HUMAN":("RuntimeTelemetryLog","human_oversight_rate"),
    "IND-FAIR-DATA":("ModelCard","data_diversity_entropy"),
    "IND-ROB-TEST":("RedTeamingReport","test_coverage"),
    "IND-ETH-COV":("ModelCard","ethical_assessment_coverage"),
}
AGI_SPECIFIC = {"IND-TRANS-AI-ID","IND-CTRL-CEASE-RATE","IND-CTRL-CEASE-LATENCY",
                "IND-CTRL-SLO-RATE","IND-CTRL-SLO-VIOLATIONS"}
STAGE = {"ModelCard":"deployment","RedTeamingReport":"evaluation",
         "RuntimeTelemetryLog":"operation","SelfLearningAuditRecord":"operation","IncidentReport":"operation"}
NORMS=["N-TRANS-AI-ID","N-TRANS-EXP","N-CTRL-CEASE","N-CTRL-SLO","N-ACC-HUMAN","N-FAIR-DATA","N-ROB-TEST","N-ETH-COV"]

# (conservative_value, generous_value, source_note). None = absent.
# Majority-resolved mapping: only the robustness-testing proxy has majority support.
P_ROB = (None, 0.95, "PROXY (illustrative value): documented adversarial-evaluation suite with reported quantitative scope; NOT the norm's required test-category-coverage fraction. Consensus of 3 coders; see reconciliation_log.md.")

CARDS = {
 # ---- PRIOR generation (2024) ----
 "OpenAI GPT-4o (2024 system card)":{"gen":"prior","url":"https://cdn.openai.com/gpt-4o-system-card.pdf",
   "types":{"conservative":{"ModelCard"},"generous":{"ModelCard","RedTeamingReport"}},
   "fields":{"IND-ROB-TEST":P_ROB}},
 "Anthropic Claude 3.5 Sonnet (2024 model card)":{"gen":"prior","url":"https://www-cdn.anthropic.com/fed9cc193a14b84131812372d8d5857f8f304c52/Model_Card_Claude_3_Addendum.pdf",
   "types":{"conservative":{"ModelCard"},"generous":{"ModelCard","RedTeamingReport"}},
   "fields":{"IND-ROB-TEST":P_ROB}},
 "Meta Llama 3.1 (2024 model card)":{"gen":"prior","url":"https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md",
   "types":{"conservative":{"ModelCard"},"generous":{"ModelCard"}},"fields":{}},
 # ---- CURRENT generation (2025-26) ----
 "OpenAI GPT-5.5 (2026 system card)":{"gen":"current","url":"https://openai.com/index/gpt-5-5-system-card/",
   "types":{"conservative":{"ModelCard"},"generous":{"ModelCard","RedTeamingReport"}},
   "fields":{"IND-ROB-TEST":P_ROB}},
 "Anthropic Claude Opus 4.6 (2026 system card)":{"gen":"current","url":"https://www.anthropic.com/claude-opus-4-6-system-card",
   "types":{"conservative":{"ModelCard"},"generous":{"ModelCard","RedTeamingReport"}},
   "fields":{"IND-ROB-TEST":P_ROB}},
 "Google Gemini 3 (2025 model card + frontier safety)":{"gen":"current","url":"https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf",
   "types":{"conservative":{"ModelCard"},"generous":{"ModelCard","RedTeamingReport"}},
   "fields":{"IND-ROB-TEST":P_ROB}},
}

def build_bundle(card, mode):
    b={t:{"confidence":0.9,"lifecycle_stage":STAGE[t],"provenance":card["url"]} for t in card["types"][mode]}
    idx=0 if mode=="conservative" else 1
    for ind,(art,field) in INDICATORS.items():
        if art in b and ind in card["fields"] and card["fields"][ind][idx] is not None:
            b[art][field]=card["fields"][ind][idx]
    return b

def covered(card, mode):
    idx=0 if mode=="conservative" else 1
    pop=[i for i in INDICATORS if i in card["fields"] and card["fields"][i][idx] is not None and INDICATORS[i][0] in card["types"][mode]]
    return pop, [i for i in pop if i in AGI_SPECIFIC]

results={"study":"real-evidence bridgeability, prior vs current generations (coverage, NOT auditor-confirmed compliance)","mapping":"three-coder majority resolution (see reconciliation_log.md)","engine_version":"1.4","cards":{}}
gens={"prior":{}, "current":{}}
for name,card in CARDS.items():
    results["cards"][name]={"generation":card["gen"],"url":card["url"]}
    for mode in ("conservative","generous"):
        bundle=build_bundle(card,mode)
        rep=run_compliance_check(name,"public_evidence",mode,bundle)
        verdicts={nv.norm_id:nv.verdict.value for nv in rep.norms}
        pop,agi=covered(card,mode)
        r={"artifact_types":len(card["types"][mode]),"indicators":len(pop),"indicators_list":pop,
           "agi_specific":len(agi),"norms_evaluable":sum(1 for v in verdicts.values() if v!="EVIDENCE_GAP"),
           "evaluable_norms":[n for n,v in verdicts.items() if v!="EVIDENCE_GAP"],"norm_verdicts":verdicts}
        results["cards"][name][mode]=r
        g=gens[card["gen"]].setdefault(mode,{"types":0,"ind":0,"agi":0,"norms":0})
        g["types"]+=r["artifact_types"]; g["ind"]+=r["indicators"]; g["agi"]+=r["agi_specific"]; g["norms"]+=r["norms_evaluable"]
results["by_generation"]=gens
json.dump(results, open(os.path.join(os.path.dirname(__file__),"public_study_results.json"),"w"), indent=2)

def line(label, g): 
    return (f"  {label:12s} artifact-types {g['types']:2d}/15 | indicators {g['ind']:2d}/30 | "
            f"AGI-specific {g['agi']:2d}/15 | norms evaluable {g['norms']:2d}/24")
print("REAL-EVIDENCE BRIDGEABILITY  —  PRIOR (2024) vs CURRENT (2025-26)\n"+"="*70)
for gen in ("prior","current"):
    names=[n for n in CARDS if CARDS[n]["gen"]==gen]
    print(f"\n{gen.upper()} generation: {', '.join(n.split(' (')[0] for n in names)}")
    for mode in ("conservative","generous"):
        print(line(f"[{mode}]", gens[gen][mode]))
print("\n"+"="*70+"\nDELTA (current - prior)")
for mode in ("conservative","generous"):
    p,c=gens["prior"][mode],gens["current"][mode]
    print(f"  [{mode:11s}] artifact-types {c['types']-p['types']:+d} | indicators {c['ind']-p['ind']:+d} | "
          f"AGI-specific {c['agi']-p['agi']:+d} | norms evaluable {c['norms']-p['norms']:+d}")
