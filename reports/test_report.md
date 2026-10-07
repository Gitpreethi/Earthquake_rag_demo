# RAG test report

Run: 2026-10-06T02:37:24  
Answer engine: extractive / none (evidence sentences only)

| Metric | Value |
|---|---|
| queries | 17 |
| hit_at_k | 1.0 |
| mrr | 1.0 |
| mean_source_recall | 1.0 |
| abstention_rate_on_out_of_scope | 0.5 |
| status_match_rate | 0.765 |
| mean_latency_ms | 76.5 |

Hit@k / MRR / source recall are computed on queries with expected sources; abstention rate on the out-of-scope queries (status 'insufficient' or a question entity absent from the corpus).

## H1 (historical): What information is available about the 2001 Gujarat earthquake?

_Note: Current corpus has no dedicated 2001 Kutch/Bhuj document (KUTCH 2001.pdf not yet added); only a reference to 'Gujarat earthquake lessons' and the 2016-2024 NCS catalogue for Gujarat._

**Status:** partial (expected partial / insufficient) | best vector cosine 0.7939 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected earthquake-sikkireco, National Center of Seismology)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Earthquake catalogue summary for Gujarat (India) – source: Official Website of National Center of Seismology. [E1]
> - Earthquake events recorded in Gujarat, India (events 1–10 of 164): [E2]
> - Earthquake catalogue summary for Haryana (India) – source: Official Website of National Center of Seismology. [E3]
> - Earthquake catalogue summary for Haryana – source: Official Website of National Center of Seismology. [E4]
> - Implementation Strategy (adapted from Gujarat Earthquake Lessons) The implementation strategy, which harmonizes the emergency nature of reconstruction program with a strong emphasis on community participation and seismic safety measures against mountain settlements. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Official Website of National Center of Seismology | Sheet 'Sheet1', 164 rows summarised | Gujarat | 1.00 | 0.7916 | 10.498 | yes |
| E2 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 70–507 | Gujarat | 0.93 | 0.7894 | 10.783 | yes |
| E3 | Official Website of National Center of Seismology | Sheet 'Sheet1', 108 rows summarised | Haryana | 0.44 | 0.752 | – | yes |
| E4 | Official Website of National Center of Seismology | Sheet 'Sheet1', 54 rows summarised | Haryana | 0.43 | 0.7486 | – | yes |
| E5 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 38–39 | Introduction | 0.39 | – | 10.603 | yes |
| E6 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 55–56 | Documentation Of Sikkim Earthquake 2011 | 0.38 | – | 8.014 |  |
| E7 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 6 | Contents | 0.37 | – | 3.679 |  |
| E8 | NDRF Standard Operating Procedure on Earthquake | p. 6 | 1. Introduction | 0.36 | – | 3.639 |  |

## H2 (historical): When did the 2011 Sikkim earthquake occur and what was its magnitude?

**Status:** partial (expected answered) | best vector cosine 0.8262 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected earthquake-sikkireco)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Chandan Ghosh, Professor and Head and Dr Surya Parkash, Associate Professor, Geohazards Division, to document the Mw6.9 Sikkim Earthquake that struck on Sunday, 18 September 2011, at 18:10:48 hrs (IST). [E1]
> - The Fateful Sunday – Sept 18, 2011 On Sunday, 18 September 2011 at 6:11PM (local time), a Mw 6.9 earthquake with an epicenter located near the Sikkim-Nepal border region (27.723°N, 88.064°E), killed 77 people, including 16 at the Teesta Stage III Hydroelectric power project site, injured 719, left thousands homeless, and temporarily displaced many and also caused substantial loss to livestock. [E2]
> - Earthquakes in the last two centuries have already caused approximately $3.14 trillion (2011 HNDECI-Adjusted int. dollars) damage (of this around 20% has occurred in 2011, mostly due to Tohoku earthquake, Japan). [E3]
> - Progressive: Ongoing long-term development progress is maintained, and long term community goals are not sacrificed for short-term individual benefits Importance of Damage survey – first few days Immediately after and during the first few days after the earthquake, thousands of buildings may result damaged, while new shocks can still occur. [E4]
> - Be aware that some earthquakes are actually foreshocks, and a larger earthquake might occur. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 3–4 | Contents | 0.93 | 0.8189 | 12.391 | yes |
| E2 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 11 | Introduction | 0.91 | 0.8262 | 11.662 | yes |
| E3 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 6 | Contents | 0.79 | 0.7916 | 12.288 | yes |
| E4 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 17 | Introduction | 0.50 | – | 15.491 | yes |
| E5 | NDRF Standard Operating Procedure on Earthquake | pp. 6–7 | 1. Introduction | 0.49 | – | 14.147 | yes |
| E6 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 5874–6355 | Sikkim | 0.48 | 0.8117 | – |  |
| E7 | NDRF Standard Operating Procedure on Earthquake | p. 3 | Ndrf • India | 0.48 | – | 13.669 |  |
| E8 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 4566–4764 | Sikkim | 0.48 | 0.8094 | – |  |

## H3 (historical): Which were the strongest earthquakes recorded in India in the National Center of Seismology catalogue?

**Status:** partial (expected answered / partial) | best vector cosine 0.8049 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected National Center of Seismology)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Earthquake catalogue summary for Chhattisgarh (India) – source: Official Website of National Center of Seismology. [E1]
> - Earthquake catalogue summary for Chandigarh (India) – source: Official Website of National Center of Seismology. [E2]
> - Earthquake catalogue summary for Goa (India) – source: Official Website of National Center of Seismology. [E3]
> - Earthquake catalogue summary for Bihar (India) – source: Official Website of National Center of Seismology. [E4]
> - Earthquake catalogue summary for Karnataka (India) – source: Official Website of National Center of Seismology. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Official Website of National Center of Seismology | Sheet 'Sheet1', 50 rows summarised | Chhattisgarh | 1.00 | 0.7913 | 20.614 | yes |
| E2 | Official Website of National Center of Seismology | Sheet 'Sheet1', 12 rows summarised | Chandigarh | 1.00 | 0.7859 | 20.689 | yes |
| E3 | Official Website of National Center of Seismology | Sheet 'Sheet1', 1 rows summarised | Goa | 1.00 | 0.7771 | 24.365 | yes |
| E4 | Official Website of National Center of Seismology | Sheet 'Sheet1', 3 rows summarised | Bihar | 1.00 | 0.7792 | 22.449 | yes |
| E5 | Official Website of National Center of Seismology | Sheet 'Sheet1', 55 rows summarised | Karnataka | 1.00 | 0.7856 | 20.651 | yes |
| E6 | Official Website of National Center of Seismology | Sheet 'Sheet1', 10 rows summarised | Kerala | 1.00 | 0.7854 | 20.651 |  |
| E7 | Official Website of National Center of Seismology | Sheet 'Sheet1', 1 rows summarised | Lakshadweep Island | 0.99 | 0.7721 | 24.065 |  |
| E8 | Official Website of National Center of Seismology | Sheet 'Sheet1', 10 rows summarised | Tamil Nadu | 0.98 | 0.7834 | 20.539 |  |

## P1 (policy): What does the Disaster Management Act 2005 say about disaster management?

**Status:** partial (expected answered / partial) | best vector cosine 0.8427 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected DM-Act-2005)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - 53 OF 2005 [23rd December, 2005.] An Act to provide for the effective management of disasters and for matters connected therewith or incidental thereto. [E1]
> - The Disaster Management Act, 2005 (Act No. [E2]
> - The Disaster Management Bill, 2005 provides for setting up of a National Disaster Management Authority under the Chairmanship of the Prime Minister, State Disaster Management Authorities under the Chairmanship of the Chief Ministers and District Disaster Management Authorities under the Chairmanship of District Magistrates. [E3]
> - The Government have decided to enact a law on disaster management to provide for requisite institutional mechanisms for drawing up and monitoring the implementation of the disaster management plans, ensuring measures by various wings of Government for prevention and mitigating effects of disasters and for undertaking a holistic, coordinated and prompt response to any disaster situation. [E4]
> - Powers and functions of District Authority.—(1) The District Authority shall act as the district planning, coordinating and implementing body for disaster management and take all measures for the purposes of disaster management in the district in accordance with the guidelines laid down by the National Authority and the State Authority. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | The Disaster Management Act, 2005 | p. 6 | Chapter XI – Miscellaneous › The Disaster Manageme | 1.00 | 0.8427 | 22.616 | yes |
| E2 | The Disaster Management Act, 2005 | pp. 1–2 | Amending Acts | 0.98 | 0.8236 | 22.436 | yes |
| E3 | The Disaster Management Act, 2005 | p. 39 | Chapter XI – Miscellaneous › Statement Of Objects  | 0.96 | 0.8044 | 21.025 | yes |
| E4 | The Disaster Management Act, 2005 | p. 39 | Chapter XI – Miscellaneous › Statement Of Objects  | 0.89 | 0.8184 | 20.304 | yes |
| E5 | The Disaster Management Act, 2005 | pp. 19–20 | Chapter IV – District Disaster Management Authorit | 0.88 | 0.7806 | 20.532 | yes |
| E6 | The Disaster Management Act, 2005 | p. 6 | Chapter I – Preliminary › Section 1. Short title,  | 0.86 | 0.7985 | 20.271 |  |
| E7 | The Disaster Management Act, 2005 | pp. 26–27 | Chapter V – Measures By The Government For Disaste | 0.83 | 0.7702 | 20.457 |  |
| E8 | The Disaster Management Act, 2005 | p. 28 | Chapter VII – National Instituteof Disaster Manage | 0.82 | 0.7555 | 20.905 |  |

## P2 (policy): What are the powers and functions of the District Disaster Management Authority?

**Status:** partial (expected answered) | best vector cosine 0.8606 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected DM-Act-2005)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Powers and functions of District Authority in the event of any threatening disaster situation or disaster. [E1]
> - Powers and functions of District Authority.—(1) The District Authority shall act as the district planning, coordinating and implementing body for disaster management and take all measures for the purposes of disaster management in the district in accordance with the guidelines laid down by the National Authority and the State Authority. [E2]
> - Powers of Chairperson of District Authority.—(1) The Chairperson of the District Authority shall, in addition to presiding over the meetings of the District Authority, exercise and discharge such powers and functions of the District Authority as the District Authority may delegate to him. [E3]
> - Powers and functions of District Authority in the event of any threatening disaster situation or disaster.—For the purpose of assisting, protecting or providing relief to the community, in response to any threatening disaster situation or disaster, the District Authority may— [E4]
> - (xxix) perform such other functions as the State Government or State Authority may assign to it or as it deems necessary for disaster management in the District. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | The Disaster Management Act, 2005 | pp. 3–4 | Chapter IV – District Disaster Management Authorit | 0.99 | 0.8432 | 29.096 | yes |
| E2 | The Disaster Management Act, 2005 | pp. 19–20 | Chapter IV – District Disaster Management Authorit | 0.98 | 0.8606 | 27.971 | yes |
| E3 | The Disaster Management Act, 2005 | p. 19 | Chapter IV – District Disaster Management Authorit | 0.93 | 0.814 | 28.6 | yes |
| E4 | The Disaster Management Act, 2005 | p. 22 | Chapter IV – District Disaster Management Authorit | 0.93 | 0.8339 | 25.431 | yes |
| E5 | The Disaster Management Act, 2005 | p. 21 | Chapter IV – District Disaster Management Authorit | 0.92 | 0.8316 | 26.943 | yes |
| E6 | The Disaster Management Act, 2005 | p. 20 | Chapter IV – District Disaster Management Authorit | 0.92 | 0.8351 | 25.325 |  |
| E7 | The Disaster Management Act, 2005 | p. 20 | Chapter IV – District Disaster Management Authorit | 0.89 | 0.8323 | 24.901 |  |
| E8 | The Disaster Management Act, 2005 | pp. 14–15 | Chapter III – State Disaster Management Authoritie | 0.88 | 0.8029 | 26.506 |  |

## P3 (policy): How is the National Disaster Response Force constituted under the DM Act?

**Status:** partial (expected answered) | best vector cosine 0.869 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected DM-Act-2005)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - National Disaster Response Force.—(1) There shall be constituted a National Disaster Response Force for the purpose of specialist response to a threatening disaster situation or disaster. [E1]
> - (2) Subject to the provisions of this Act, the State Disaster Response Force shall be constituted in such manner, with such functions and the terms and conditions of service of the members of such Force shall be such as may be prescribed by the State Government concerned.] [E2]
> - It provides for constitution of a National Disaster Response Force and setting up the National Institute of Disaster Management. [E3]
> - (l) "National Plan" means the plan for disaster management for the whole of the country prepared under section 11; [E4]
> - NDRF National Disaster Response Force 2. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | The Disaster Management Act, 2005 | p. 29 | Chapter VIII – 2[Disaster Response Force] › Sectio | 1.00 | 0.869 | 40.334 | yes |
| E2 | The Disaster Management Act, 2005 | p. 29 | Chapter VIII – 2[Disaster Response Force] › Sectio | 0.98 | 0.815 | 35.039 | yes |
| E3 | The Disaster Management Act, 2005 | p. 39 | Chapter XI – Miscellaneous › Statement Of Objects  | 0.93 | 0.806 | 27.197 | yes |
| E4 | The Disaster Management Act, 2005 | p. 8 | Chapter I – Preliminary › Section 2. Definitions | 0.93 | 0.805 | 27.224 | yes |
| E5 | NDRF Standard Operating Procedure on Earthquake | pp. 4–5 | Ndrf • India › 8.5 De-Activation Phase | 0.41 | – | 22.453 | yes |
| E6 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 28 | Introduction | 0.38 | – | 21.028 |  |
| E7 | The Disaster Management Act, 2005 | p. 4 | Chapter VI – Local Authorities | 0.93 | 0.7842 | 30.188 |  |
| E8 | The Disaster Management Act, 2005 | p. 29 | Chapter VIII – 2[Disaster Response Force] › Sectio | 0.91 | 0.7813 | 29.701 |  |

## P4 (policy): What is the punishment for a false warning under the Disaster Management Act?

**Status:** partial (expected answered) | best vector cosine 0.8725 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected DM-Act-2005)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Punishment for false warning.—Whoever makes or circulates a false alarm or warning as to disaster or its severity or magnitude, leading to panic, shall on conviction, be punishable with imprisonment which may extend to one year or with fine. [E1]
> - Punishment for false claim.—Whoever knowingly makes a claim which he knows or has reason to believe to be false for obtaining any relief, assistance, repair, reconstruction or other benefits consequent to disaster from any officer of the Central Government, the State Government, the National Authority, the State Authority 3[, the District Authority or the Urban Authority], shall, on conviction be  [E2]
> - Punishment for false warning. [E3]
> - (a) obstructs any officer or employee of the Central Government or the State Government, or a person authorised by the National Authority or State Authority or District Authority 1[or Urban Authority] in the discharge of his functions under this Act; or [E4]
> - Pre-disaster database, Forecasting, Warning Training & capacity building of community Enforcement of Codes, guidelines Damage & Loss assessment Rehabilitation phase Immediate relief & rescue Disaster Impact (Earthquake) & landslides Institutionalization of DM and developments Typological, dimensional and functional data Evaluation and assessment of loss Road map for long term reconstructions Post- [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | The Disaster Management Act, 2005 | p. 31 | Chapter X – Offences And Penalties › Section 54. P | 1.00 | 0.8725 | 37.469 | yes |
| E2 | The Disaster Management Act, 2005 | p. 31 | Chapter X – Offences And Penalties › Section 52. P | 0.98 | 0.8016 | 30.138 | yes |
| E3 | The Disaster Management Act, 2005 | pp. 4–5 | Chapter IX – Finance, Accounts And Audit | 0.98 | 0.8005 | 35.765 | yes |
| E4 | The Disaster Management Act, 2005 | p. 31 | Chapter X – Offences And Penalties › Section 51. P | 0.90 | 0.7205 | 17.3 | yes |
| E5 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 56 | Post Event | 0.38 | – | 10.895 | yes |
| E6 | The Disaster Management Act, 2005 | p. 32 | Chapter X – Offences And Penalties › Section 60. C | 0.89 | 0.7496 | 14.199 |  |
| E7 | The Disaster Management Act, 2005 | p. 25 | Chapter V – Measures By The Government For Disaste | 0.88 | 0.6982 | 17.451 |  |
| E8 | The Disaster Management Act, 2005 | p. 32 | Chapter X – Offences And Penalties › Section 58. O | 0.88 | 0.7138 | 15.244 |  |

## L1 (location): What earthquake information is available for Sikkim?

**Status:** partial (expected answered / partial) | best vector cosine 0.8628 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected earthquake-sikkireco, National Center of Seismology)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - It is not a post-earthquake discovery that Sikkim lies in the severe seismic zone of India. [E1]
> - Chandan Ghosh, Professor and Head and Dr Surya Parkash, Associate Professor, Geohazards Division, to document the Mw6.9 Sikkim Earthquake that struck on Sunday, 18 September 2011, at 18:10:48 hrs (IST). [E2]
> - earthquakes are not new to the Sikkim; its history is teeming with deadly tremors. [E3]
> - Lessons from Sikkim Earthquake – status check [E4]
> - Earthquake events recorded in Sikkim, India (events 151–160 of 203): [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 7 | Contents | 0.85 | 0.83 | 8.092 | yes |
| E2 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 3–4 | Contents | 0.82 | 0.8099 | 7.938 | yes |
| E3 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 17–18 | Introduction | 0.76 | 0.8095 | 7.747 | yes |
| E4 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 13 | Introduction | 0.75 | 0.7962 | 7.731 | yes |
| E5 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 6697–7564 | Sikkim | 0.50 | 0.8628 | – | yes |
| E6 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 3054–3982 | Sikkim | 0.49 | 0.8601 | – |  |
| E7 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 29 | Introduction | 0.50 | – | 8.173 |  |
| E8 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 1489–1717 | Sikkim | 0.48 | 0.8594 | – |  |

## L2 (location): Which earthquakes have been recorded in Uttarakhand?

**Status:** partial (expected answered / partial) | best vector cosine 0.8653 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected National Center of Seismology)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Earthquake events recorded in Uttarakhand, India (events 511–520 of 587): [E1]
> - Earthquake events recorded in Uttarakhand, India (events 311–320 of 587): [E2]
> - Earthquake events recorded in Uttarakhand, India (events 571–580 of 587): [E3]
> - Earthquake events recorded in Uttarakhand, India (events 71–80 of 587): [E4]
> - Earthquake events recorded in Uttarakhand, India (events 201–210 of 587): [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 8773–8849 | Uttarakhand | 0.87 | 0.8653 | 9.696 | yes |
| E2 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 7423–7496 | Uttarakhand | 0.87 | 0.8568 | 9.705 | yes |
| E3 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 9714–9934 | Uttarakhand | 0.84 | 0.8591 | 9.696 | yes |
| E4 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 1603–1694 | Uttarakhand | 0.84 | 0.8555 | 9.705 | yes |
| E5 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 5680–5803 | Uttarakhand | 0.79 | 0.853 | 9.705 | yes |
| E6 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 8472–8582 | Uttarakhand | 0.79 | 0.8557 | 9.687 |  |
| E7 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 7357–7413 | Uttarakhand | 0.78 | 0.8499 | 9.714 |  |
| E8 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 8150–8197 | Uttarakhand | 0.78 | 0.8489 | 9.714 |  |

## L3 (location): What seismic activity has been recorded around the Andaman and Nicobar Islands?

**Status:** partial (expected answered / partial) | best vector cosine 0.8556 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected National Center of Seismology)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Earthquake events recorded in Andaman and Nicobar Islands, India (events 101–110 of 668): [E1]
> - Earthquake events recorded in Andaman and Nicobar Islands, India (events 71–80 of 668): [E2]
> - Earthquake Forecasting Exercise – IMD to come upto people's expectation India Meteorological Department (IMD) is the nodal agency of Government of India responsible for monitoring seismic activity in and around the country. [E3]
> - Earthquake events recorded in Andaman and Nicobar Islands, India (events 421–430 of 668): [E4]
> - Earthquake events recorded in Andaman and Nicobar Islands, India (events 521–530 of 668): [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 1230–1358 | Andaman and Nicobar Islands | 0.97 | 0.8556 | 20.697 | yes |
| E2 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 842–990 | Andaman and Nicobar Islands | 0.96 | 0.8528 | 20.708 | yes |
| E3 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 19 | Introduction | 0.50 | – | 22.927 | yes |
| E4 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 3884–4089 | Andaman and Nicobar Islands | 0.92 | 0.8555 | 20.666 | yes |
| E5 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 6308–6468 | Andaman and Nicobar Islands | 0.88 | 0.8516 | 20.666 | yes |
| E6 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 9718–9927 | Andaman and Nicobar Islands | 0.88 | 0.8489 | 20.804 |  |
| E7 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 3758–3883 | Andaman and Nicobar Islands | 0.86 | 0.8492 | 20.687 |  |
| E8 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 7511–7810 | Andaman and Nicobar Islands | 0.85 | 0.8499 | 20.676 |  |

## M1 (multi_document): What emergency response information is present in the knowledge base?

**Status:** partial (expected answered / partial) | best vector cosine 0.7007 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected DM-Act-2005, Eartrhquake)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - (g) require any Ministry or Department or agency of the Government to make available to the Central Government or State Government such men or material resources as are available with it for the purposes of emergency response, rescue and relief; [E1]
> - An ambulance equipped with BLS equipment, DM medicines along with required stores shall be prepared and taken along by USAR Team for disaster response. [E2]
> - (xvii) ensure that the Departments of the Government at the district level and the local authorities prepare their response plans in accordance with the district response plan; [E3]
> - National Disaster Response Force.—(1) There shall be constituted a National Disaster Response Force for the purpose of specialist response to a threatening disaster situation or disaster. [E4]
> - State Disaster Response Force.—(1) The State Government may, by notification in the Official Gazette, constitute a State Disaster Response Force for the purpose of specialist response to a threatening disaster situation or disaster. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | The Disaster Management Act, 2005 | pp. 12–13 | Chapter II – The National Disaster Management Auth | 0.96 | 0.6995 | 9.853 | yes |
| E2 | NDRF Standard Operating Procedure on Earthquake | pp. 9–10 | 8. Execution Of The Earthquake Disaster Response › | 0.88 | 0.6514 | 9.963 | yes |
| E3 | The Disaster Management Act, 2005 | p. 20 | Chapter IV – District Disaster Management Authorit | 0.83 | 0.6743 | 5.36 | yes |
| E4 | The Disaster Management Act, 2005 | p. 29 | Chapter VIII – 2[Disaster Response Force] › Sectio | 0.83 | 0.6602 | 6.061 | yes |
| E5 | The Disaster Management Act, 2005 | p. 29 | Chapter VIII – 2[Disaster Response Force] › Sectio | 0.83 | 0.6598 | 6.132 | yes |
| E6 | NDRF Standard Operating Procedure on Earthquake | p. 7 | 3. Purpose | 0.70 | 0.6342 | 5.281 |  |
| E7 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 37 | Introduction | 0.50 | – | 10.916 |  |
| E8 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 4 | Contents | 0.49 | – | 10.323 |  |

## M2 (multi_document): How do NDRF search and rescue procedures relate to the legal role of the National Disaster Response Force?

**Status:** partial (expected answered / partial) | best vector cosine 0.7799 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected Eartrhquake, DM-Act-2005)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - National Disaster Response Force.—(1) There shall be constituted a National Disaster Response Force for the purpose of specialist response to a threatening disaster situation or disaster. [E1]
> - This document describes a high level concept of search & rescue operations for ensuring an integrated response to damaging earthquake impacting India involving SDRF, Civil Defence & Home Guards and other stakeholders. [E2]
> - Directorate General National Disaster Response Force Ministry of Home Affairs 9th Floor, Paryavaran Bhawan, CGO Complex, Lodhi Road, New Delhi-110003 Phone: 24363260 • Fax: 24363261 Website: www.ndrfandcd.gov.in Design & Print by : kam@kamstudio.net [E3]
> - While disaster response, the primary tasks of the NDRF shall remain focused towards ensuring the rescue, safety and protection of the disaster victims entrapped under the debris or entangled in any other life threatening situation. [E4]
> - In case, an earthquake disaster involves deployment of Team of a Battalion in its AOR only, the State/District Authorities shall identify the most likely arrival point of responding Team(s) of the NDRF or other agencies and to establish 'Reception Departure Centre' (RDC) appropriately in view of arrival whether by road/rail/air. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | The Disaster Management Act, 2005 | p. 29 | Chapter VIII – 2[Disaster Response Force] › Sectio | 0.96 | 0.7304 | 44.701 | yes |
| E2 | NDRF Standard Operating Procedure on Earthquake | p. 3 | Ndrf • India | 0.94 | 0.7799 | 36.947 | yes |
| E3 | NDRF Standard Operating Procedure on Earthquake | pp. 38–40 | Rescue Operation | 0.88 | 0.7113 | 42.563 | yes |
| E4 | NDRF Standard Operating Procedure on Earthquake | p. 16 | Sitrep. › 8.4 Operation Phase | 0.87 | 0.7292 | 33.377 | yes |
| E5 | NDRF Standard Operating Procedure on Earthquake | p. 12 | (Hadr) : › 8.3 Mobilisation Phase | 0.86 | 0.7372 | 27.182 | yes |
| E6 | The Disaster Management Act, 2005 | pp. 12–13 | Chapter II – The National Disaster Management Auth | 0.75 | 0.697 | 27.207 |  |
| E7 | The Disaster Management Act, 2005 | pp. 10–11 | Chapter II – The National Disaster Management Auth | 0.69 | 0.6966 | 24.312 |  |
| E8 | The Disaster Management Act, 2005 | p. 29 | Chapter VIII – 2[Disaster Response Force] › Sectio | 0.48 | – | 41.296 |  |

## M3 (multi_document): What lessons from the Sikkim earthquake are relevant to earthquake search and rescue response teams?

**Status:** partial (expected answered / partial) | best vector cosine 0.8468 | relevance gate passed

**Retrieval:** hit=True, first relevant rank=1, source recall=1.0 (expected earthquake-sikkireco, Eartrhquake)

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - The team carried reconnaissance survey of the affected areas from 21 to 25 September 2011 and held interactions with officials from the State and Central Government Agencies, armed forces, communities, NGOs and civil societies involved in the relief and rescue operations. [E1]
> - Lessons from Sikkim earthquake – status check [E2]
> - Earthquake induced damage potential on the Hydropower projects in the Sikkim state required to be evaluated by a special team. [E3]
> - for Long term recovery Sikkim Earthquake & landslides [Sept 18, 2011] Response, Rescue , Debris clearance Damage and Loss assessment air & struction pa ns air st [E4]
> - Each USAR team should be comprised of all components of the team such as Management, Operation, Search, Rescue and Logistics. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 4 | Contents | 0.95 | 0.8254 | 23.081 | yes |
| E2 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 2–3 | National Institute Of Disaster Management | 0.84 | 0.8468 | 16.986 | yes |
| E3 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 34 | Introduction | 0.83 | 0.8025 | 20.859 | yes |
| E4 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 9–10 | Road Map | 0.82 | 0.8122 | 18.224 | yes |
| E5 | NDRF Standard Operating Procedure on Earthquake | p. 9 | 8. Execution Of The Earthquake Disaster Response › | 0.50 | – | 28.881 | yes |
| E6 | NDRF Standard Operating Procedure on Earthquake | p. 9 | 8. Execution Of The Earthquake Disaster Response › | 0.46 | – | 22.797 |  |
| E7 | NDRF Standard Operating Procedure on Earthquake | p. 3 | Ndrf • India | 0.46 | – | 22.791 |  |
| E8 | NDRF Standard Operating Procedure on Earthquake | p. 12 | (Hadr) : › 8.3 Mobilisation Phase | 0.44 | – | 21.466 |  |

## I1 (insufficient): Summarize the earthquake information available in the ISRO data.

_Note: No ISRO document is in the current corpus._

**Status:** insufficient (expected insufficient / partial) | best vector cosine 0.7508 | relevance gate passed | absent from corpus: ISRO

**Answer:**

> ⚠ The knowledge base contains no passage mentioning: ISRO. The sentences below are only related material, not an answer.
> 
> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Such systems provide a means for modern urban regions to cope effectively with the aftermath of major earthquakes and, in some cases, they may even provide warning, seconds before the arrival of seismic waves (Kanamori, et al, 1997). [E1]
> - Earthquake catalogue summary for Oman – source: Official Website of National Center of Seismology. [E2]
> - Earthquake catalogue summary for Odisha (India) – source: Official Website of National Center of Seismology. [E3]
> - Earthquake catalogue summary for Uzbekistan – source: Official Website of National Center of Seismology. [E4]
> - Earthquake catalogue summary for Sri Lanka – source: Official Website of National Center of Seismology. [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 19 | Introduction | 0.85 | 0.7289 | 3.492 | yes |
| E2 | Official Website of National Center of Seismology | Sheet 'Sheet1', 23 rows summarised | Oman | 0.57 | 0.7508 | – | yes |
| E3 | Official Website of National Center of Seismology | Sheet 'Sheet1', 15 rows summarised | Odisha | 0.57 | 0.7436 | – | yes |
| E4 | Official Website of National Center of Seismology | Sheet 'Sheet1', 30 rows summarised | Uzbekistan | 0.56 | 0.7377 | – | yes |
| E5 | Official Website of National Center of Seismology | Sheet 'Sheet1', 8 rows summarised | Sri Lanka | 0.52 | 0.7318 | – | yes |
| E6 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 6 | Contents | 0.50 | – | 3.679 |  |
| E7 | NDRF Standard Operating Procedure on Earthquake | p. 6 | 1. Introduction | 0.49 | – | 3.639 |  |
| E8 | NDRF Standard Operating Procedure on Earthquake | pp. 1–3 | Ndrf • India | 0.48 | – | 3.618 |  |

## I2 (insufficient): What is the recipe for a chocolate cake?

**Status:** insufficient (expected insufficient) | best vector cosine 0.414 | relevance gate blocked

**Answer:**

> The knowledge base does not contain enough evidence to answer this question. The closest retrieved passages are shown below for transparency, but none of them is relevant enough to support an answer.

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | NDRF Standard Operating Procedure on Earthquake | pp. 29–30 | 10. Conclusion | 0.50 | 0.414 | – |  |
| E2 | NDRF Standard Operating Procedure on Earthquake | p. 24 | 10. Conclusion | 0.49 | 0.4071 | – |  |
| E3 | The Disaster Management Act, 2005 | p. 37 | Chapter XI – Miscellaneous › Section 78. Power of  | 0.46 | 0.3938 | – |  |
| E4 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 43 | Documentation Of Sikkim Earthquake 2011 | 0.46 | 0.3922 | – |  |
| E5 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 35 | Introduction | 0.44 | 0.3852 | – |  |
| E6 | The Disaster Management Act, 2005 | p. 37 | Chapter XI – Miscellaneous › Section 77. Rules and | 0.44 | 0.3839 | – |  |
| E7 | The Disaster Management Act, 2005 | p. 33 | Chapter XI – Miscellaneous › Section 61. Prohibiti | 0.43 | 0.3829 | – |  |
| E8 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 7 | Contents | 0.42 | 0.3795 | – |  |

## I3 (insufficient): How many people died in the 2015 Nepal earthquake?

_Note: Catalogue starts in Feb 2016 and has no casualty figures._

**Status:** partial (expected insufficient / partial) | best vector cosine 0.7246 | relevance gate passed

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - Earthquake events recorded in Nepal (events 51–60 of 174): [E1]
> - Earthquake events recorded in Nepal (events 61–70 of 174): [E2]
> - The Fateful Sunday – Sept 18, 2011 On Sunday, 18 September 2011 at 6:11PM (local time), a Mw 6.9 earthquake with an epicenter located near the Sikkim-Nepal border region (27.723°N, 88.064°E), killed 77 people, including 16 at the Teesta Stage III Hydroelectric power project site, injured 719, left thousands homeless, and temporarily displaced many and also caused substantial loss to livestock. [E3]
> - Scientific publications have warned that severe earthquakes are likely to occur anytime in the Himalayan Region, which could adversely affect the lives of several million people in India. [E4]
> - In addition about $200 million US damage was caused in Tibet (China), and slightly higher in Eastern Nepal in addition to losses in Bhutan with around 6000 buildings damaged. [Cumulative deaths and economic losses related to global 2011-dollar GDP (PPP) and population, (source Daniell et al, CATDAT -2011)] [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 3197–3354 | Nepal | 0.94 | 0.7246 | 10.602 | yes |
| E2 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 3355–3653 | Nepal | 0.93 | 0.7215 | 10.609 | yes |
| E3 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 11 | Introduction | 0.87 | 0.6813 | 19.367 | yes |
| E4 | NDRF Standard Operating Procedure on Earthquake | p. 3 | Ndrf • India | 0.85 | 0.6559 | 15.071 | yes |
| E5 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 6–7 | Contents | 0.80 | 0.718 | 10.197 | yes |
| E6 | Sikkim Earthquake (2011)- Reconstruction Strategy | pp. 36–37 | Introduction | 0.49 | – | 17.565 |  |
| E7 | Official Website of National Center of Seismology | Sheet 'Sheet1', 10000 rows summarised | Catalogue overview | 0.40 | 0.6317 | – |  |
| E8 | Sikkim Earthquake (2011)- Reconstruction Strategy | p. 6 | Contents | 0.40 | 0.7118 | – |  |

## I4 (insufficient): What is the tsunami evacuation procedure for the Kerala coast?

**Status:** partial (expected insufficient / partial) | best vector cosine 0.6922 | relevance gate passed

**Answer:**

> **Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim from the retrieved evidence (not a synthesised answer):
> 
> - 2018-07-09 12:52:18 IST | M3.3 (ML) | depth 10 km | lat 12.576, lon 75.586 | 81km NNE of Kannur, Kerala, India [E1]
> - 2021-04-29 15:37:35 IST | M2.8 (ML) | depth 10 km | lat 7.995, lon 76.684 | 65km SSW of Thiruvananthapuram, Kerala, India [E2]
> - (iv) carrying out evacuation of persons or live-stock from an area of any threatening disaster situation or disaster; [E3]
> - The objective of this SOP is to establish operating procedures for addressing all aspects of management during earthquake disasters. [E4]
> - 2[(ga) "evacuation" means moving people or assets temporarily to safer places before, during or after the occurrence of a hazardous event; [E5]

**Retrieved sources:**

| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |
|---|---|---|---|---|---|---|---|
| E1 | Official Website of National Center of Seismology | Sheet 'Sheet1', 10 rows summarised | Kerala | 1.00 | 0.6837 | 13.389 | yes |
| E2 | Official Website of National Center of Seismology | Sheet 'Sheet1', rows 1372–9363 | Kerala | 1.00 | 0.6922 | 13.975 | yes |
| E3 | The Disaster Management Act, 2005 | p. 26 | Chapter V – Measures By The Government For Disaste | 0.90 | 0.6531 | 10.075 | yes |
| E4 | NDRF Standard Operating Procedure on Earthquake | p. 7 | 4. Objectives | 0.89 | 0.6659 | 5.149 | yes |
| E5 | The Disaster Management Act, 2005 | p. 7 | Chapter I – Preliminary › Section 2. Definitions | 0.87 | 0.6508 | 7.013 | yes |
| E6 | The Disaster Management Act, 2005 | p. 7 | Chapter I – Preliminary › Section 2. Definitions | 0.86 | 0.6467 | 7.342 |  |
| E7 | NDRF Standard Operating Procedure on Earthquake | pp. 23–24 | 10. Conclusion | 0.83 | 0.6469 | 5.268 |  |
| E8 | NDRF Standard Operating Procedure on Earthquake | p. 7 | 3. Purpose | 0.81 | 0.6413 | 5.405 |  |
