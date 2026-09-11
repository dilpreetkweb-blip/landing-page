from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, Table, TableStyle, Image,
                                NextPageTemplate, KeepTogether)

FD = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("DJ", FD + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("DJ-B", FD + "LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DJ-I", FD + "LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("DJ-BI", FD + "LiberationSans-BoldItalic.ttf"))
# without this, inline <b> and <i> tags silently render as regular weight
pdfmetrics.registerFontFamily("DJ", normal="DJ", bold="DJ-B", italic="DJ-I", boldItalic="DJ-BI")

NAVY  = HexColor("#122738")
BLUE  = HexColor("#1D5C99")
GOLD  = HexColor("#B8860B")
GOLDL = HexColor("#FFD166")
BODY  = HexColor("#3A4557")
MUTED = HexColor("#6B7687")
LIGHT = HexColor("#F4F6F9")
RULE  = HexColor("#D8DEE7")

PW, PH = letter
M = 0.85 * inch
CW = PW - 2 * M

S = dict(
    h1=ParagraphStyle("h1", fontName="DJ-B", fontSize=17, leading=21, textColor=NAVY,
                      spaceBefore=20, spaceAfter=3, keepWithNext=1),
    kicker=ParagraphStyle("kicker", fontName="DJ-B", fontSize=8.5, leading=11, textColor=GOLD,
                          spaceBefore=20, spaceAfter=2, keepWithNext=1),
    h2=ParagraphStyle("h2", fontName="DJ-B", fontSize=12, leading=16, textColor=NAVY,
                      spaceBefore=13, spaceAfter=4, keepWithNext=1),
    p=ParagraphStyle("p", fontName="DJ", fontSize=10, leading=15.5, textColor=BODY,
                     spaceAfter=8),
    li=ParagraphStyle("li", fontName="DJ", fontSize=10, leading=15.5, textColor=BODY,
                      leftIndent=15, bulletIndent=3, spaceAfter=4),
    note=ParagraphStyle("note", fontName="DJ", fontSize=9, leading=13.5, textColor=MUTED,
                        spaceAfter=7),
    callout=ParagraphStyle("callout", fontName="DJ", fontSize=10, leading=15.5, textColor=NAVY,
                           spaceAfter=0),
    th=ParagraphStyle("th", fontName="DJ-B", fontSize=9, leading=12.5, textColor=white),
    td=ParagraphStyle("td", fontName="DJ", fontSize=9, leading=12.5, textColor=BODY),
    tdb=ParagraphStyle("tdb", fontName="DJ-B", fontSize=9, leading=12.5, textColor=NAVY),
    cta=ParagraphStyle("cta", fontName="DJ-B", fontSize=13, leading=17, textColor=white,
                       alignment=TA_CENTER),
)

def P(t, s="p"):
    return Paragraph(t, S[s])

def BL(items):
    return [Paragraph(t, S["li"], bulletText="•") for t in items]

def NL(items):
    return [Paragraph(f"<b>{i+1}.</b>  {t}", S["li"]) for i, t in enumerate(items)]

def link(url, text):
    return f'<link href="{url}" color="#1D5C99"><u>{text}</u></link>'

def callout(html, bg=LIGHT, bar=GOLDL):
    inner = Table([[Paragraph(html, S["callout"])]], colWidths=[CW - 0.34 * inch])
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, -1), bg),
    ]))
    outer = Table([["", inner]], colWidths=[0.055 * inch, CW - 0.055 * inch])
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), bar),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [Spacer(1, 4), outer, Spacer(1, 11)]

def table(rows, widths, align_left_first=True):
    data = [[Paragraph(c, S["th"]) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(r[0], S["tdb"])] + [Paragraph(c, S["td"]) for c in r[1:]])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 1), (-1, -1), 0.6, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
    ]
    t.setStyle(TableStyle(style))
    return [Spacer(1, 3), t, Spacer(1, 12)]

# ---------------------------------------------------------------- pages
def cover_page(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, 0, 0.16 * inch, PH, fill=1, stroke=0)

    c.setFillColor(GOLDL)
    c.setFont("DJ-B", 10)
    t = "FREE GUIDE"
    c.drawCentredString(PW / 2, PH - 2.55 * inch, " ".join(t))

    c.setFillColor(white)
    c.setFont("DJ-B", 37)
    c.drawCentredString(PW / 2, PH - 3.45 * inch, "The AME Canada")
    c.drawCentredString(PW / 2, PH - 4.03 * inch, "Roadmap")

    c.setFillColor(GOLDL)
    c.rect(PW / 2 - 0.62 * inch, PH - 4.45 * inch, 1.24 * inch, 2.2, fill=1, stroke=0)

    c.setFillColor(HexColor("#C9D6E3"))
    c.setFont("DJ", 13)
    c.drawCentredString(PW / 2, PH - 4.95 * inch,
                        "How to become an Aircraft Maintenance Engineer")
    c.drawCentredString(PW / 2, PH - 5.24 * inch, "in Canada — and how to actually get started")

    c.setFillColor(HexColor("#8FA3B8"))
    c.setFont("DJ", 10.5)
    c.drawCentredString(PW / 2, 1.62 * inch, "Written by Dilpreet")
    c.setFont("DJ", 9)
    c.drawCentredString(PW / 2, 1.32 * inch,
                        "Aircraft maintenance apprentice  ·  Sharing the path, not selling a shortcut")
    c.restoreState()

def body_page(c, doc):
    c.saveState()
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(M, 0.72 * inch, PW - M, 0.72 * inch)
    c.setFillColor(MUTED)
    c.setFont("DJ", 8)
    c.drawString(M, 0.53 * inch, "The AME Canada Roadmap")
    c.drawRightString(PW - M, 0.53 * inch, str(c.getPageNumber() - 1))
    c.restoreState()

# ---------------------------------------------------------------- story
DIAG = "/tmp/claude-0/-home-user-landing-page/70629628-72c9-56b7-812c-bb091a1b055d/scratchpad/pathway-diagram.png"
PRODUCT = "https://dilpreet-2.kit.com/products/ame-career-system"

st = [NextPageTemplate("body"), Spacer(1, 1), PageBreak()]

def H(num, title):
    if num > 1:
        st.append(PageBreak())
    st.append(Paragraph(f"S E C T I O N &nbsp;{num}", S["kicker"]))
    st.append(Paragraph(title, S["h1"]))
    st.append(Spacer(1, 5))

# 1
H(1, "Welcome — Why I Made This")
st += [P("Hi, I'm Dilpreet."),
       P("I came to Canada in 2022. I completed an 18-month aircraft maintenance program at "
         "Centennial College, and I'm now working as an apprentice, building the experience and "
         "logbook entries I need to earn my AME licence."),
       P("I'm still on this path. I haven't finished it. That's exactly why I'm writing this."),
       P("After one of my Instagram Reels reached over 250,000 people, my inbox filled with the "
         "same questions over and over: <i>How do I become an AME? What education do I need? "
         "Can you refer me? Where do I even start?</i>")]
st += callout("Let me answer the referral one first, clearly: <b>I'm not a recruiter, and I can't "
              "refer anyone into my company.</b> What I can do is share what I've actually learned "
              "— the path as I've experienced it, what worked, what I got wrong, and what I wish "
              "someone had told me in 2022.")
st += [P("That's what this roadmap is. Not official guidance. Not a shortcut. Just an honest map "
         "from someone a few steps ahead of you."),
       P("<b>How to use this:</b> read it start to finish once, then come back to the sections you "
         "need. The last section gives you a 30-day plan so this doesn't become one more thing you "
         "read and forget.")]

# 2
H(2, "What Is an AME?")
st += [P("An <b>Aircraft Maintenance Engineer (AME)</b> is a licensed professional responsible for "
         "maintaining, inspecting, and repairing aircraft — and critically, for <b>signing the "
         "maintenance release</b> that certifies an aircraft is airworthy."),
       P("That signature is the heart of the job. When an AME signs, they are personally certifying "
         "that the work meets standard and the aircraft is safe to fly. It's a licensed trade for "
         "the same reason medicine is licensed: the consequences of getting it wrong are severe."),
       Paragraph("What the day-to-day actually looks like", S["h2"])]
st += BL(["Scheduled inspections and servicing",
          "Troubleshooting faults — often under time pressure, often at odd hours",
          "Component removal, repair, and installation",
          "Reading and following maintenance manuals precisely",
          "Documentation — a great deal of it, and it matters as much as the wrench work"])
st += [Paragraph("Where AMEs work", S["h2"])]
st += BL(["Airlines — scheduled and line maintenance",
          "MROs (Maintenance, Repair and Overhaul organizations)",
          "Regional and charter operators",
          "General aviation — flight schools, private operators",
          "Helicopter operators",
          "Manufacturing and aerospace support"])
st += [Spacer(1, 4),
       P("<b>What the career actually looks like:</b> you start as an apprentice or helper working "
         "under a licensed AME. You build experience, log it, write exams, and eventually get "
         "licensed yourself. From there the path can branch — type ratings on specific aircraft, "
         "lead hand and supervisory roles, quality assurance, technical services, or training."),
       P("It's a hands-on trade with real responsibility, shift work, and a genuine skill ceiling. "
         "It is not a desk job and it's not a quick one.")]

# 3
H(3, "The Canadian AME Categories")
st += [P("Canada's AME licence is issued in <b>ratings</b> — you don't get a single generic \"AME "
         "licence,\" you get a licence with specific ratings on it.")]
st += table([["Rating", "What it covers"],
             ["M1", "Non-turbojet aircraft with a maximum certified take-off weight below "
                    "12,566 lbs (5,700 kg) — smaller general aviation aircraft"],
             ["M2", "All aircraft not covered by M1 — including turbine-powered aircraft and all "
                    "helicopters, regardless of weight"],
             ["E", "Aircraft electronic systems — communications, navigation, autoflight, "
                   "instruments, electrical elements of other systems, and structural work directly "
                   "associated with maintaining those systems"],
             ["S", "Aircraft structures — airframe structural inspection and repair"]],
            [0.95 * inch, CW - 0.95 * inch])
st += callout("<b>A useful detail:</b> holders of either an M1 or M2 rating also carry maintenance "
              "release privileges for all turbine-powered helicopters and SFAR 41C aeroplanes, "
              "including their variants and derivatives.")
st += [Paragraph("How people typically choose", S["h2"])]
st += BL(["<b>M</b> is the broadest and most common starting point — the general aircraft "
          "maintenance path",
          "<b>E</b> suits people drawn to electronics, avionics, and diagnostic work",
          "<b>S</b> suits people drawn to structural and composite repair work"])
st += [Spacer(1, 4),
       P("You are not locked in forever. Ratings can be added later. But your choice shapes which "
         "training program you enroll in, so it's worth thinking about early rather than defaulting "
         "into one.")]

# 4
H(4, "The Canadian Pathway, Step by Step")
st += [P("Here is the honest shape of the path. Note that there are <b>two routes</b>, and most "
         "online advice only ever mentions one."),
       Spacer(1, 6),
       Image(DIAG, width=6.35 * inch, height=6.35 * 1330 / 2000 * inch),
       Spacer(1, 14),
       Paragraph("The experience requirement", S["h2"])]
st += table([["Rating", "Total experience", "Specialty", "On civil-registered aircraft"],
             ["M or E", "48 months", "12 months", "6 months"],
             ["S", "36 months", "24 months", "6 months"]],
            [1.5 * inch, 1.75 * inch, 1.5 * inch, CW - 4.75 * inch])
st += [P("<b>Route A — approved training program.</b> You complete a Transport Canada–approved "
         "diploma, which earns you roughly <b>18 months of credit</b> toward that total. You still "
         "complete the remaining ~30 months as real on-the-job experience afterward."),
       P("<b>Route B — direct entry.</b> You skip the diploma and build all 48 (or 36) months "
         "through work. It's slower on paper and harder to break into without training, but it is a "
         "legitimate route and worth knowing exists."),
       Paragraph("The other requirements, regardless of route", S["h2"])]
st += BL(["<b>Task list</b> — you must have performed at least <b>70% of the applicable items in "
          "Appendix B of Airworthiness Manual (AWM) 566</b> for your rating",
          "<b>Exams</b> — the technical knowledge exam(s) for your category, plus the "
          "<b>Regulatory Requirements (CAR)</b> exam. Transport Canada's official study guide is "
          "<b>TP 14038</b>",
          "<b>Minimum age</b> — you must be <b>21</b> for licence issuance",
          "<b>Citizenship</b> — you must prove citizenship of <i>some</i> country; it does "
          "<b>not</b> have to be Canadian",
          "<b>Application</b> — <b>Form 24-0083</b>, with original or certified documents"])
st += callout("<b>About your logbook — start it on day one.</b><br/><br/>Your experience is proven "
              "through a personal logbook (or equivalent, such as signed employer letters) recording "
              "exact dates, the work performed, and the aircraft type. This is what you eventually "
              "submit to Transport Canada.<br/><br/>I cannot overstate this: the day you touch your "
              "first aircraft in a working capacity, start logging. People lose months of credit "
              "because they started logging late or logged sloppily.")

# 5
H(5, "Education & Training Options")
st += [P("These are Transport Canada–approved programs I verified while researching this roadmap:")]
st += table([["School", "Category", "Experience credit"],
             ["BCIT (British Columbia)", "M", "18 months"],
             ["Centennial College (Ontario)", "M", "18 months"],
             ["Canadore College (Ontario)", "M", "18 months"],
             ["Mohawk College (Ontario)", "M", "18 months"],
             ["SAIT (Alberta)", "M", "18 months"],
             ["Fanshawe College (Ontario)", "M", "18 months"],
             ["RRC Polytech (Manitoba)", "M", "19 months"]],
            [3.3 * inch, 1.2 * inch, CW - 4.5 * inch])
st += [P("BCIT also offers separate <b>Category E</b> (approximately 68 weeks) and "
         "<b>Category S</b> (approximately 10 months) diploma programs."),
       Paragraph("Read this before you pick one", S["h2"])]
st += BL(["<b>Verify everything directly with the school.</b> Program availability, duration, "
          "tuition, and admission requirements change. Do not enroll based on this table, a blog "
          "post, or a Reddit thread — confirm on the institution's own website or with their "
          "admissions office.",
          "<b>Credit is often conditional.</b> SAIT, for example, requires 95% attendance and "
          "minimum 70% in each course to grant the 18-month credit. Showing up and passing is not "
          "automatically enough. Check the conditions at your school.",
          "<b>Admission requirements vary.</b> Canadore, for instance, requires OSSD or equivalent "
          "with Grade 12 English and Grade 12 Math. BCIT requires demonstrated English proficiency. "
          "Others differ."])
st += [Spacer(1, 4)]
st += callout("<b>A note on education terminology:</b> this roadmap uses Canadian terms — "
              "\"Grade 12\" or \"high school completion.\" If you're coming from India, that "
              "generally corresponds to completing +2 / Class 12. But do <b>not</b> assume that "
              "completing +2 automatically qualifies you for every AME program. Each institution "
              "sets its own admission requirements, including subject prerequisites and English "
              "proficiency. Check them individually.")

# 6
H(6, "A Note for International Students")
st += [P("This section matters, and I want to be careful with it."),
       P("<b>Two separate systems.</b> Your AME licence and your immigration status are governed by "
         "two completely different authorities, and confusing them causes real problems:")]
st += BL(["<b>Transport Canada</b> decides licensing. As noted, the licence requires proof of "
          "citizenship of <i>any</i> country — it does not require Canadian citizenship.",
          "<b>IRCC (Immigration, Refugees and Citizenship Canada)</b> decides who is legally allowed "
          "to work in Canada. That's a separate question with separate rules."])
st += [Spacer(1, 4)]
st += callout("<b>You do not need the licence to start working.</b> This surprises a lot of people. "
              "You can work as an <b>apprentice or helper</b> under the supervision of a licensed "
              "AME while building the experience toward your own licence. The licence is the "
              "destination, not the entry ticket.")
st += [P("<b>But you do need valid work authorization for that apprentice role.</b> That could be a "
         "Post-Graduation Work Permit, or another type of work permit, or permanent residence — it "
         "depends entirely on your situation. Eligibility rules for these change, and they changed "
         "meaningfully as recently as this year."),
       P("<b>So here's my honest position:</b> I am not an immigration consultant and I will not "
         "guess at your eligibility. Confirm your specific situation directly at "
         f"{link('https://www.canada.ca', 'canada.ca')} / IRCC, or with a licensed immigration "
         "professional. Nothing in this roadmap should be treated as immigration advice, and no "
         "program — at any school — guarantees a work permit, permanent residence, or employment.")]

# 7
H(7, "Getting Your First Aviation Experience")
st += [P("The hardest part isn't the exams. It's getting through the door the first time."),
       Paragraph("Realistic entry points", S["h2"])]
st += BL(["<b>Apprentice / helper roles</b> at maintenance organizations — the most direct route",
          "<b>MROs</b> — often more open to inexperienced candidates than airlines",
          "<b>Regional and charter operators</b> — smaller teams, more willing to train",
          "<b>General aviation</b> — flight schools and small operators, where you'll touch a wide "
          "variety of work",
          "<b>Helicopter operators</b> — a distinct and often underserved corner of the industry"])
st += [Spacer(1, 4)]
st += callout("<b>A tactic that works, and that I've watched work:</b> apply for <i>any</i> "
              "legitimate job inside an airport — ramp, ground handling, cargo, fuelling, customer "
              "service. Some people I studied with got airport jobs during their program and used "
              "them as a foot in the door.<br/><br/>Why this works: you're physically inside the "
              "environment. You meet people. You hear about openings before they're posted. You "
              "learn how an airport actually operates. It's not an AME job and I won't pretend it "
              "is — but it's proximity, and proximity in this industry compounds.")
st += [P("<b>One caution:</b> no specific route guarantees employment. What I'm describing is how "
         "people commonly get in, not a formula that always produces a job.")]

# 8
H(8, "Finding Your First Aviation Job")
st += [Paragraph("Where to look", S["h2"])]
st += BL(["<b>Employer career pages</b> — check these directly and regularly; many roles never "
          "reach the big boards",
          "<b>LinkedIn</b> — more on this in the next section, because it's not just a job board",
          "<b>Indeed</b> — volume, but real postings",
          "<b>Aviation-specific job boards</b>",
          "<b>Direct outreach</b> — emailing maintenance managers at organizations you'd like to "
          "work for",
          "<b>Networking</b> — instructors, classmates, anyone already inside the industry"])
st += [Spacer(1, 4),
       P("<b>Job titles to search for:</b> Apprentice Aircraft Maintenance Engineer, Aircraft "
         "Maintenance Apprentice, Aircraft Maintenance Helper, Aviation Maintenance Technician, AME "
         "Apprentice. The same job wears different titles at different companies — search broadly."),
       Paragraph("How to approach employers when you have limited experience", S["h2"])]
st += BL(["Be specific about where you are: your program, your credit toward the licence, your "
          "category",
          "Be clear about what you're asking for — an apprentice or entry-level role, not a "
          "licensed position",
          "Keep it short. Maintenance managers are busy people who read email between tasks",
          "Follow up once, about 5–7 days later. Once. Not four times"])

# 9
H(9, "How to Stand Out in a Competitive Market")
st += [P("This is the section I most wish someone had given me in 2022.")]
st += callout("Here's the uncomfortable truth: <b>everyone graduating from your program has the same "
              "diploma you do.</b> Same courses, same credit, same certificate. On paper, you are "
              "interchangeable with your entire graduating class. Technical skill gets you "
              "considered. It does not get you chosen.")
st += [P("What separates people is the stuff nobody tests you on."),
       P("<b>Build your LinkedIn — and build it early.</b> Not a resume mirror. A real profile: a "
         "clear headline saying what you are and what you're working toward, your program, your "
         "category, what you're looking for. Then actually use it — follow aviation companies, "
         "engage with people in the industry, connect with classmates and instructors. Recruiters "
         "and hiring managers genuinely look here."),
       Paragraph("Soft skills carry more weight than people expect", S["h2"])]
st += BL(["<b>Communication</b> — including spoken English confidence. You'll be explaining faults, "
          "reading back instructions, and writing documentation that other people's safety depends on",
          "<b>Problem-solving</b> — troubleshooting is the job. Not following steps; figuring out "
          "what's actually wrong",
          "<b>Reliability</b> — showing up, on time, consistently. In an industry built on trust, "
          "this is not a small thing",
          "<b>Teamwork</b> — you're rarely working alone, and hangars are tight-knit environments"])
st += [Spacer(1, 4),
       P("<b>Adaptability and fresh thinking.</b> Aviation maintenance is a traditional industry "
         "with deeply established practices — for good reasons. But there's real value in someone "
         "who can apply new tools and new thinking to old processes without being reckless about "
         "it. Being the person who improves how something is done, rather than just executing it, "
         "gets noticed."),
       P("<b>Personal brand.</b> How you're perceived before you ever apply. How you talk about "
         "aviation publicly, how you carry yourself, what your online presence says about you. It's "
         "quieter than the other factors but it compounds over years."),
       P("<b>EQ and IQ both matter.</b> Technical intelligence gets you the interview. Emotional "
         "intelligence — self-awareness, composure under pressure, taking feedback without "
         "defensiveness, reading a room — gets you the job, and matters even more for everything "
         "that comes after it."),
       Paragraph("What I got wrong", S["h2"]),
       P("I'll be direct about my own mistakes, because they cost me time."),
       P("<b>I didn't build my LinkedIn early enough, and I didn't start applying fast enough.</b> "
         "I waited. I told myself I'd start properly once I felt ready."),
       P("After I graduated, I was working in a restaurant. Mind-numbing, exhausting work I didn't "
         "want to be doing, in a field I'd just spent 18 months training to leave. And I stayed "
         "there longer than I should have."),
       P("Eventually I quit. I committed fully: LinkedIn and Indeed, <b>two to three applications a "
         "day, sometimes five</b>. Head down. Focused entirely on the applying itself — not on "
         "outcomes, not on responses, not on whether any individual application went anywhere.")]
st += callout("<b>Within two months, I had an apprenticeship offer.</b><br/><br/>That's the whole "
              "lesson. Not talent, not connections. Volume, consistency, and detaching from the "
              "outcome long enough to keep going. Nail your resume, then apply relentlessly and let "
              "the numbers work.<br/><br/><b>If I could do it, you can too.</b>")

# 10
H(10, "Resume & Application Basics")
st += [Paragraph("What belongs on an aviation-oriented resume", S["h2"])]
st += BL(["<b>Education</b> — your program, institution, dates, and your Transport Canada "
          "experience credit",
          "<b>Technical training</b> — systems you've worked on, specific coursework that's relevant",
          "<b>Technical skills</b> — airframe, powerplant, electrical, hydraulics, whatever applies",
          "<b>Hands-on experience</b> — including non-aviation mechanical work; it counts for more "
          "than you think",
          "<b>Tools and equipment</b> — what you're actually proficient with",
          "<b>Certifications</b> — safety training, WHMIS, anything relevant",
          "<b>Transferable skills</b> — if you've worked in any environment demanding precision, "
          "safety awareness, or accountability, that's relevant"])
st += [Spacer(1, 4),
       P("<b>What employers actually care about:</b> safety mindset, attention to detail, "
         "reliability, and whether you can follow procedure precisely. Demonstrate these through "
         "specifics, not adjectives. \"Maintained 100% documentation accuracy across X\" beats "
         "\"detail-oriented.\""),
       Paragraph("Common resume mistakes", S["h2"])]
st += BL(["Sending the identical resume to 50 companies",
          "Burying your Transport Canada credit where nobody sees it — it's one of the most "
          "relevant facts about you",
          "Listing responsibilities instead of what you actually did",
          "Typos. In an industry built on precision, a typo is a signal",
          "Making it long. One page, two at absolute most"])

# 11
H(11, "Interview Preparation")
st += [Paragraph("Before the interview", S["h2"])]
st += BL(["Research the employer — what aircraft do they operate? Airline, MRO, charter, general "
          "aviation? Their fleet shapes their work",
          "Read the job description properly and map your experience to it",
          "Prepare specific examples, not general claims"])
st += [Spacer(1, 4),
       P("<b>What gets asked</b> — and these are illustrative examples, not a guaranteed list:")]
st += BL(["<b>Technical questions</b> about systems, procedures, or troubleshooting approach",
          "<b>Behavioural questions</b> — a time you caught a mistake, handled pressure, disagreed "
          "with someone, or worked through something difficult"])
st += [Spacer(1, 4),
       P("<b>How to handle limited experience.</b> Don't apologize for it and don't inflate it. Say "
         "where you are honestly, then show what you've done with what you've had. \"I haven't "
         "worked on that type yet, but here's how I approached something similar, and here's how "
         "I'd go about learning it\" is a strong answer. Pretending to know something you don't is "
         "disqualifying in this industry — and rightly so, because safety depends on people "
         "admitting what they don't know."),
       P("<b>What they're really assessing:</b> safety mindset, whether you'll admit uncertainty "
         "rather than guess, reliability, attention to detail, communication, and willingness to "
         "learn. Much of the interview is a character assessment wearing technical clothing.")]

# 12
H(12, "Common Mistakes to Avoid")
st += NL(["<b>Confusing the Canadian AME licence with the American A&amp;P certificate.</b> These "
          "are different systems, different regulators, different requirements. The FAA's Airframe "
          "&amp; Powerplant certificate is not a Canadian AME licence and doesn't convert "
          "automatically. A lot of the advice you'll find online is American — check the source "
          "before you act on it.",
          "<b>Assuming the diploma is the licence.</b> It isn't. A Transport Canada–approved program "
          "gives you training and roughly 18 months of experience credit toward a 48-month "
          "requirement. The licence comes after the remaining experience, the task list, and the exams.",
          "<b>Starting your logbook late, or keeping it badly.</b> Your logbook is your evidence. "
          "Incomplete entries cost you real months.",
          "<b>Choosing a program without checking where it leads.</b> Confirm it's Transport "
          "Canada–approved, confirm the category it leads to, and confirm the conditions on the "
          "experience credit.",
          "<b>Waiting until graduation to build connections.</b> Build your network and your "
          "LinkedIn while you're still studying. I learned this one the expensive way.",
          "<b>Applying randomly without tailoring.</b> Volume matters — but volume of <i>tailored</i> "
          "applications. Not the same thing as spraying an identical PDF everywhere.",
          "<b>Conflating licensing with immigration status.</b> Two different systems, two different "
          "authorities. Getting this wrong leads to expensive, avoidable decisions.",
          "<b>Treating social media as official guidance.</b> Including this roadmap. I've "
          "researched what's here carefully, but Transport Canada is the authority — not me, and "
          "not anyone on TikTok.",
          "<b>Relying on outdated information.</b> Requirements, programs, and policies change. "
          "Something true in 2019 may be wrong today."])

# 13
H(13, "Your First 30 Days")
st += [P("Information without action is just entertainment. Here's a concrete plan."),
       Paragraph("Days 1–7 — Decide", S["h2"])]
st += BL(["Finish reading this roadmap",
          "Choose your target category (M1 / M2 / E / S)",
          "Decide: approved training program, or direct-entry route",
          "Write the decision down. Vague intentions don't survive contact with real life"])
st += [Paragraph("Days 8–14 — Research", S["h2"])]
st += BL(["Shortlist 3–5 schools or programs",
          "Confirm current admission requirements with each one <b>directly</b>",
          "Note application deadlines",
          "If you're an international student, confirm your work authorization situation at IRCC"])
st += [Paragraph("Days 15–21 — Build", S["h2"])]
st += BL(["Write your resume — first draft, not a perfect one",
          "Set up or overhaul your LinkedIn profile",
          "Start a list of target employers in your region"])
st += [Paragraph("Days 22–30 — Move", S["h2"])]
st += BL(["Start applying. Track every application",
          "Reach out directly to at least 3 employers or industry contacts",
          "Follow up on anything you sent in week three",
          "Review what happened and set your next 30-day target"])
st += [Spacer(1, 6)]
st += callout("Focus on the action, not the outcome. You control how many quality applications you "
              "send. You don't control response times. That distinction is the entire difference "
              "between people who make it in and people who quit at month two.")

# 14
H(14, "Important Disclaimer")
st += [P("This roadmap is for <b>general educational purposes</b> and is based on publicly "
         "available information and my personal experience."),
       P("Requirements, programs, licensing processes, and employment conditions <b>change</b>. "
         "Always verify current requirements directly with Transport Canada, the relevant "
         "educational institution, employer, or other official authority before making decisions."),
       P("This roadmap is <b>not</b> official Transport Canada guidance and implies no affiliation "
         "with Transport Canada, any airline, employer, or training institution."),
       P("I am <b>not</b> a recruiter, an immigration consultant, or an official representative of "
         "any regulatory body. This roadmap does not provide company referrals and does not "
         "guarantee licensing, employment, or immigration outcomes."),
       Paragraph("Official sources you should use", S["h2"])]
st += BL([f"Transport Canada — Aircraft Maintenance Engineer licensing: "
          f"{link('https://tc.canada.ca', 'tc.canada.ca')}",
          f"Government of Canada / IRCC — immigration: "
          f"{link('https://www.canada.ca', 'canada.ca')}",
          "Individual institution websites — for program and admission requirements"])

# 15
H(15, "Your Next Step: The AME Career System")
st += [P("You now have the map. The harder part is executing it consistently over months."),
       P("That's what I built the <b>AME Career System</b> for — a Notion workspace that turns "
         "everything in this roadmap into a working system:")]
st += BL(["<b>Step-by-Step AME Checklist</b> — the whole journey in order, checked off as you go",
          "<b>School &amp; Program Tracker</b> — compare programs by category, duration, experience "
          "credit, tuition, and deadlines",
          "<b>Employer Tracker</b> — who you've contacted, who you haven't, when to follow up",
          "<b>Job Application Tracker</b> — every application with source, status, and follow-up date",
          "<b>Resume &amp; Application Templates</b> — aviation resume outline, cold outreach email, "
          "follow-up message, LinkedIn note",
          "<b>Your First 30 Days Action Plan</b> — week by week"])
st += [Spacer(1, 16)]

btn_label = Paragraph(f'<link href="{PRODUCT}" color="#FFFFFF">Get the AME Career System  →</link>',
                      S["cta"])
btn = Table([[btn_label]], colWidths=[3.9 * inch], rowHeights=[0.52 * inch])
btn.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), BLUE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
wrap = Table([[btn]], colWidths=[CW])
wrap.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                          ("LEFTPADDING", (0, 0), (-1, -1), 0),
                          ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
st += [wrap, Spacer(1, 20),
       P("And if you never buy anything — genuinely, I hope this roadmap was useful on its own. "
         "That was the point of writing it."),
       Spacer(1, 10),
       P("Good luck out there."),
       Spacer(1, 6),
       Paragraph("— Dilpreet", ParagraphStyle("sig", fontName="DJ-B", fontSize=11, leading=15,
                                              textColor=NAVY))]

# ---------------------------------------------------------------- build
OUT = "/home/user/landing-page/The-Free-AME-Canada-Roadmap.pdf"
doc = BaseDocTemplate(OUT, pagesize=letter,
                      leftMargin=M, rightMargin=M, topMargin=0.8 * inch, bottomMargin=0.95 * inch,
                      title="The Free AME Canada Roadmap",
                      author="Dilpreet",
                      subject="How to become an Aircraft Maintenance Engineer in Canada")
frame = Frame(M, 0.95 * inch, CW, PH - 0.8 * inch - 0.95 * inch, id="f")
doc.addPageTemplates([
    PageTemplate(id="cover", frames=[frame], onPage=cover_page),
    PageTemplate(id="body", frames=[frame], onPage=body_page),
])
doc.build(st)
print("built:", OUT)
