"""
Verbal ability — hand-written (language can't be generated reliably).

Each entry lists the correct option first; options are shuffled with a
fixed seed when the bank is built so the answer letter varies.
"""

import random
from string import ascii_uppercase

SYN = "Choose the word closest in meaning to **{w}**."
ANT = "Choose the word most nearly **opposite** in meaning to **{w}**."
OWS = "Choose the one word for: *{w}*"
IDIOM = "Choose the meaning of the idiom: *“{w}”*"

# (slug, kind, prompt, [correct, wrong, wrong, wrong], difficulty, explanation)
VOCABULARY = [
    # ---- easy
    ("voc-abundant", SYN, "ABUNDANT", ["Plentiful", "Scarce", "Abandoned", "Absent"], "easy", "**Abundant** means existing in large quantities — *plentiful*. *Scarce* is its opposite."),
    ("voc-ancient", ANT, "ANCIENT", ["Modern", "Old", "Antique", "Historic"], "easy", "**Ancient** means very old; the opposite is *modern*. The other options are near-synonyms."),
    ("voc-brief", SYN, "BRIEF", ["Short", "Long", "Bright", "Brave"], "easy", "**Brief** means lasting a short time or using few words — *short*."),
    ("voc-courage", SYN, "COURAGE", ["Bravery", "Fear", "Anger", "Caution"], "easy", "**Courage** is the ability to face danger or difficulty — *bravery*."),
    ("voc-expand", ANT, "EXPAND", ["Contract", "Enlarge", "Extend", "Explain"], "easy", "**Expand** means to become larger; the opposite is *contract* (become smaller)."),
    ("voc-fragile", SYN, "FRAGILE", ["Delicate", "Sturdy", "Fragrant", "Flexible"], "easy", "**Fragile** means easily broken — *delicate*. *Sturdy* is the opposite; *fragrant* only sounds similar."),
    ("voc-generous", ANT, "GENEROUS", ["Stingy", "Kind", "Lavish", "Giving"], "easy", "**Generous** means freely giving; the opposite is *stingy* (unwilling to give or spend)."),
    ("voc-hostile", SYN, "HOSTILE", ["Unfriendly", "Hospitable", "Peaceful", "Polite"], "easy", "**Hostile** means unfriendly or aggressive. *Hospitable* looks similar but means welcoming."),
    ("voc-humble", ANT, "HUMBLE", ["Arrogant", "Modest", "Meek", "Simple"], "easy", "**Humble** means modest about one's importance; the opposite is *arrogant*."),
    ("voc-rapid", SYN, "RAPID", ["Swift", "Slow", "Steady", "Rough"], "easy", "**Rapid** means happening quickly — *swift*."),
    ("voc-victory", ANT, "VICTORY", ["Defeat", "Triumph", "Success", "Conquest"], "easy", "**Victory** is winning; its opposite is *defeat*. The others are synonyms."),
    ("voc-vacant", SYN, "VACANT", ["Empty", "Occupied", "Vague", "Valid"], "easy", "**Vacant** means not occupied — *empty*."),
    ("voc-transparent", ANT, "TRANSPARENT", ["Opaque", "Clear", "Lucid", "Visible"], "easy", "**Transparent** means you can see through it; **opaque** means light cannot pass through."),
    ("voc-diligent", SYN, "DILIGENT", ["Hardworking", "Lazy", "Careless", "Intelligent"], "easy", "**Diligent** means showing steady, careful effort — *hardworking*. Being diligent is not the same as being *intelligent*."),
    ("voc-optimistic", ANT, "OPTIMISTIC", ["Pessimistic", "Hopeful", "Cheerful", "Positive"], "easy", "**Optimistic** means expecting good outcomes; the opposite is *pessimistic*."),
    # ---- medium
    ("voc-adversity", SYN, "ADVERSITY", ["Hardship", "Prosperity", "Opponent", "Advertisement"], "medium", "**Adversity** means difficult or unlucky circumstances — *hardship*. An *adversary* (not adversity) is an opponent."),
    ("voc-ambiguous", ANT, "AMBIGUOUS", ["Clear", "Vague", "Doubtful", "Ambitious"], "medium", "**Ambiguous** means open to more than one interpretation; the opposite is *clear*."),
    ("voc-concise", SYN, "CONCISE", ["Brief", "Lengthy", "Precise", "Confused"], "medium", "**Concise** means giving information clearly in few words — *brief*. *Precise* means exact, which is different."),
    ("voc-frugal", ANT, "FRUGAL", ["Extravagant", "Thrifty", "Careful", "Economical"], "medium", "**Frugal** means careful with money; the opposite is *extravagant* (spending too much)."),
    ("voc-prudent", SYN, "PRUDENT", ["Wise", "Rash", "Proud", "Shy"], "medium", "**Prudent** means acting with care and thought for the future — *wise*. *Rash* is the opposite."),
    ("voc-tranquil", ANT, "TRANQUIL", ["Agitated", "Calm", "Peaceful", "Serene"], "medium", "**Tranquil** means calm and peaceful; the opposite is *agitated*."),
    ("voc-lucid", SYN, "LUCID", ["Clear", "Confusing", "Lucky", "Lazy"], "medium", "**Lucid** means expressed clearly and easy to understand."),
    ("voc-verbose", ANT, "VERBOSE", ["Concise", "Wordy", "Talkative", "Verbal"], "medium", "**Verbose** means using more words than needed; the opposite is *concise*."),
    ("voc-zeal", SYN, "ZEAL", ["Enthusiasm", "Apathy", "Jealousy", "Zone"], "medium", "**Zeal** is great energy or enthusiasm for a cause. *Apathy* is the opposite."),
    ("voc-indigenous", ANT, "INDIGENOUS", ["Foreign", "Native", "Local", "Original"], "medium", "**Indigenous** means originating naturally in a place (native); the opposite is *foreign*."),
    ("voc-alleviate", SYN, "ALLEVIATE", ["Relieve", "Aggravate", "Elevate", "Allocate"], "medium", "**Alleviate** means to make pain or a problem less severe — *relieve*. *Aggravate* means to make worse."),
    ("voc-scarcity", ANT, "SCARCITY", ["Abundance", "Shortage", "Lack", "Dearth"], "medium", "**Scarcity** means shortage; the opposite is *abundance*. *Dearth* and *lack* are synonyms."),
    ("voc-ows-illiterate", OWS, "One who cannot read or write", ["Illiterate", "Ignorant", "Innocent", "Illegible"], "medium", "An **illiterate** person cannot read or write. *Ignorant* means lacking knowledge in general; *illegible* describes handwriting that can't be read."),
    ("voc-ows-optimist", OWS, "A person who always looks on the bright side", ["Optimist", "Pessimist", "Realist", "Fatalist"], "medium", "An **optimist** expects the best. A *pessimist* expects the worst; a *fatalist* believes events are fixed by fate."),
    ("voc-ows-library", OWS, "A place where books are kept for reading or borrowing", ["Library", "Laboratory", "Gallery", "Granary"], "medium", "A **library** holds books. A *gallery* displays art; a *granary* stores grain."),
    ("voc-ows-herbivores", OWS, "Animals that feed only on plants", ["Herbivores", "Carnivores", "Omnivores", "Insectivores"], "medium", "**Herbivores** eat plants; *carnivores* eat meat; *omnivores* eat both."),
    ("voc-ows-extempore", OWS, "A speech given without preparation", ["Extempore", "Eulogy", "Monologue", "Soliloquy"], "medium", "An **extempore** speech is unprepared. A *eulogy* praises someone who has died; a *soliloquy* is a character speaking thoughts aloud alone."),
    ("voc-ows-polyglot", OWS, "A person who knows many languages", ["Polyglot", "Philanthropist", "Polygamist", "Pedagogue"], "medium", "A **polyglot** speaks many languages. A *philanthropist* donates to good causes; a *pedagogue* is a teacher."),
    ("voc-idiom-bush", IDIOM, "To beat around the bush", ["To avoid coming to the point", "To search everywhere carefully", "To work very hard", "To hide from danger"], "medium", "**Beating around the bush** means talking around a topic instead of saying the main thing directly."),
    ("voc-idiom-cake", IDIOM, "A piece of cake", ["Something very easy", "Something delicious", "A small reward", "A difficult task"], "medium", "**A piece of cake** means a task that is very easy to do."),
    # ---- hard
    ("voc-garrulous", SYN, "GARRULOUS", ["Talkative", "Reserved", "Grumpy", "Gracious"], "hard", "**Garrulous** means excessively talkative, especially about trivial things."),
    ("voc-laconic", ANT, "LACONIC", ["Verbose", "Brief", "Terse", "Lazy"], "hard", "**Laconic** means using very few words; its opposite is *verbose*. *Brief* and *terse* are synonyms."),
    ("voc-obsequious", SYN, "OBSEQUIOUS", ["Servile", "Obstinate", "Obscure", "Rebellious"], "hard", "**Obsequious** means too eager to please or obey — *servile*. *Obstinate* (stubborn) only sounds similar."),
    ("voc-ebullient", ANT, "EBULLIENT", ["Subdued", "Enthusiastic", "Bubbly", "Elated"], "hard", "**Ebullient** means cheerful and full of energy; the opposite is *subdued* (quiet, restrained)."),
    ("voc-perfidious", SYN, "PERFIDIOUS", ["Treacherous", "Loyal", "Perfect", "Fearful"], "hard", "**Perfidious** means deceitful and untrustworthy — *treacherous*. *Loyal* is the opposite."),
    ("voc-sanguine", SYN, "SANGUINE", ["Optimistic", "Gloomy", "Sanitary", "Angry"], "hard", "**Sanguine** means hopeful and confident, especially in a difficult situation — *optimistic*."),
    ("voc-esoteric", ANT, "ESOTERIC", ["Well-known", "Obscure", "Mysterious", "Abstruse"], "hard", "**Esoteric** means understood by only a small group with special knowledge; the opposite is *well-known*. The other options are synonyms."),
    ("voc-ows-plutocracy", OWS, "Government by the wealthy", ["Plutocracy", "Aristocracy", "Autocracy", "Bureaucracy"], "hard", "**Plutocracy** is rule by the rich. *Aristocracy* is rule by a hereditary nobility; *autocracy* by one person with absolute power."),
    ("voc-ows-panacea", OWS, "A remedy for all diseases or problems", ["Panacea", "Placebo", "Antiseptic", "Vaccine"], "hard", "A **panacea** is a cure-all. A *placebo* is a substance with no medical effect given for psychological benefit."),
    ("voc-ows-acrophobia", OWS, "An abnormal fear of heights", ["Acrophobia", "Claustrophobia", "Hydrophobia", "Agoraphobia"], "hard", "**Acrophobia** is fear of heights. *Claustrophobia*: enclosed spaces; *hydrophobia*: water; *agoraphobia*: open or crowded places."),
]

FILL = 'Fill in the blank: "{w}"'
CORRECT = "Choose the grammatically correct sentence."
SPOT = "The sentence below is split into parts. Which part contains an error? (Choose *No error* if it is correct.)\n\n{w}"

SENTENCE_CORRECTION = [
    # ---- easy
    ("sc-good-at", FILL, "He is good ___ mathematics.", ["at", "in", "on", "with"], "easy", "The fixed expression is **good at** a subject or skill."),
    ("sc-on-time", FILL, "The train arrived ___ time; it was neither early nor late.", ["on", "in", "at", "by"], "easy", "**On time** means punctually. *In time* means early enough (before it was too late)."),
    ("sc-prefer-to", FILL, "She prefers tea ___ coffee.", ["to", "than", "against", "from"], "easy", "**Prefer** takes *to*: prefer X **to** Y. *Than* is used with *rather* (I would rather have tea than coffee)."),
    ("sc-for-years", FILL, "I have lived in Pune ___ ten years.", ["for", "since", "from", "by"], "easy", "Use **for** with a duration (ten years) and *since* with a starting point (2015)."),
    ("sc-neither-of", FILL, "Neither of the answers ___ correct.", ["is", "are", "were", "have been"], "easy", "**Neither** (of …) is singular in formal English, so it takes **is**."),
    ("sc-news-is", FILL, "The news ___ very encouraging.", ["is", "are", "were", "have been"], "easy", "**News** is an uncountable noun and takes a singular verb, despite ending in *s*."),
    ("sc-goes", FILL, "He ___ to the gym every morning.", ["goes", "go", "going", "gone"], "easy", "A habitual action in the present with a third-person singular subject: **goes**."),
    ("sc-an-honest", FILL, "She is ___ honest woman.", ["an", "a", "the", "(no article)"], "easy", "The *h* in *honest* is silent, so the word starts with a vowel sound: **an** honest woman."),
    ("sc-mathematics-is", FILL, "Mathematics ___ my favourite subject.", ["is", "are", "were", "have"], "easy", "Names of subjects ending in *-ics* (mathematics, physics, economics) take a **singular** verb."),
    ("sc-if-i-were", FILL, "If I ___ you, I would accept the offer.", ["were", "was", "am", "will be"], "easy", "Imaginary (unreal) conditions use the subjunctive **were** for every subject: *If I were you…*"),
    ("sc-go-to-bed", FILL, "The children were tired, so they went ___ bed early.", ["to", "to the", "in", "at"], "easy", "The idiom is **go to bed** — no article. *Go to the bed* means walking over to the piece of furniture."),
    ("sc-since-monday", FILL, "He has been absent ___ Monday.", ["since", "for", "from", "by"], "easy", "**Since** introduces a point in time (Monday) with the present perfect."),
    ("sc-tallest", FILL, "She is the ___ student in the class.", ["tallest", "taller", "most tall", "more taller"], "easy", "Comparing one person with the whole class needs the superlative **tallest**. *More taller* is a double comparative."),
    ("sc-discuss", FILL, "We discussed ___ the problem for an hour.", ["(no word needed)", "about", "on", "over"], "easy", "**Discuss** is transitive: you *discuss a problem*, not *discuss about* it."),
    ("sc-brother-and-i", FILL, "My brother and I ___ going to the market.", ["are", "am", "is", "was"], "easy", "Two subjects joined by *and* form a plural subject: **are**."),
    ("sc-a-lot-of-people", FILL, "There ___ a lot of people at the concert.", ["were", "was", "is", "has"], "easy", "With *a lot of* the verb agrees with the noun that follows: *people* is plural, so **were**."),
    # ---- medium
    ("sc-number-of", CORRECT, "", ["The number of applicants has increased this year.", "The number of applicants have increased this year.", "The number of applicant has increased this year.", "The numbers of applicants has increased this year."], "medium", "**The number of** + plural noun takes a **singular** verb (the subject is *number*). Compare *A number of applicants **have** applied*, which is plural."),
    ("sc-hardly-when", CORRECT, "", ["Hardly had I reached the station when the train left.", "Hardly had I reached the station than the train left.", "Hardly I had reached the station when the train left.", "Hardly had I reach the station when the train left."], "medium", "**Hardly … when** (not *than*). Starting with *Hardly* inverts the subject and auxiliary: *had I reached*."),
    ("sc-no-sooner", CORRECT, "", ["No sooner did he arrive than the meeting began.", "No sooner did he arrive when the meeting began.", "No sooner he arrived than the meeting began.", "No sooner did he arrived than the meeting began."], "medium", "**No sooner … than** (not *when*), with inversion: *did he arrive* (base form after *did*)."),
    ("sc-each-has-his", CORRECT, "", ["Each of the boys has submitted his assignment.", "Each of the boys have submitted his assignment.", "Each of the boy has submitted his assignment.", "Each of the boys have submitted their assignments."], "medium", "**Each** is singular, so the verb is **has** and the noun after *of* stays plural (*the boys*)."),
    ("sc-furniture", CORRECT, "", ["The furniture in the office is new.", "The furnitures in the office are new.", "The furniture in the office are new.", "The furnitures in the office is new."], "medium", "**Furniture** is uncountable: no plural *-s*, and it takes a singular verb (*is*)."),
    ("sc-look-forward", CORRECT, "", ["I look forward to meeting you.", "I look forward to meet you.", "I look forward for meeting you.", "I look forward to met you."], "medium", "In **look forward to**, *to* is a preposition, so it is followed by the *-ing* form: *to meeting*."),
    ("sc-one-of-those", CORRECT, "", ["He is one of those people who never give up.", "He is one of those people who never gives up.", "He is one of that people who never give up.", "He is one of those person who never give up."], "medium", "In *one of those people who…*, the relative pronoun **who** refers to *people* (plural), so the verb is **give**."),
    ("sc-scarcely-when", CORRECT, "", ["Scarcely had we started when it began to rain.", "Scarcely had we started than it began to rain.", "Scarcely we had started when it began to rain.", "Scarcely had we start when it began to rain."], "medium", "**Scarcely … when**, with inversion (*had we started*), like *hardly … when*."),
    ("sc-police-have", CORRECT, "", ["The police have arrested the thief.", "The police has arrested the thief.", "The police have arrest the thief.", "The polices have arrested the thief."], "medium", "**Police** is a plural noun in English: *the police **have***. It never takes *-s*."),
    ("sc-did-not-know", SPOT, "(A) He did not knew / (B) the answer to / (C) the last question. / (D) No error", ["(A) He did not knew", "(B) the answer to", "(C) the last question.", "(D) No error"], "medium", "After *did* (or *did not*) use the base form: *did not **know***."),
    ("sc-committee-its", SPOT, "(A) The committee / (B) have submitted / (C) its report. / (D) No error", ["(B) have submitted", "(A) The committee", "(C) its report.", "(D) No error"], "medium", "*Its report* treats the committee as a single unit, so the verb must be singular too: *has submitted*."),
    ("sc-unless-not", SPOT, "(A) Unless you do not work hard, / (B) you will not / (C) pass the exam. / (D) No error", ["(A) Unless you do not work hard,", "(B) you will not", "(C) pass the exam.", "(D) No error"], "medium", "**Unless** already means *if not*; adding *do not* makes a double negative. Correct: *Unless you work hard…*"),
    ("sc-despite-of", SPOT, "(A) Despite of the rain, / (B) the match / (C) continued as planned. / (D) No error", ["(A) Despite of the rain,", "(B) the match", "(C) continued as planned.", "(D) No error"], "medium", "**Despite** is never followed by *of*. Use *despite the rain* or *in spite of the rain*."),
    ("sc-has-returned-yesterday", SPOT, "(A) He has returned / (B) from Delhi / (C) yesterday. / (D) No error", ["(A) He has returned", "(B) from Delhi", "(C) yesterday.", "(D) No error"], "medium", "A finished past time (*yesterday*) needs the simple past: *He **returned** from Delhi yesterday*. The present perfect can't take a past time marker."),
    ("sc-neither-nor-friends", SPOT, "(A) Neither Ravi / (B) nor his friends / (C) was present at the meeting. / (D) No error", ["(C) was present at the meeting.", "(A) Neither Ravi", "(B) nor his friends", "(D) No error"], "medium", "With *neither … nor*, the verb agrees with the **nearer** subject — *his friends* (plural) → *were present*."),
    ("sc-between-you-and-me", CORRECT, "", ["Between you and me, the plan won't work.", "Between you and I, the plan won't work.", "Among you and me, the plan won't work.", "Between you and myself, the plan won't work."], "medium", "**Between** is a preposition, so it takes object pronouns: *between you and **me***. *Among* is for more than two."),
    ("sc-more-of-two", CORRECT, "", ["She is the more intelligent of the two sisters.", "She is the most intelligent of the two sisters.", "She is more intelligent of the two sisters.", "She is the intelligenter of the two sisters."], "medium", "Comparing **two** uses the comparative with *the*: *the more intelligent of the two*. The superlative is for three or more."),
    ("sc-ten-kilometres", CORRECT, "", ["Ten kilometres is a long distance to walk.", "Ten kilometres are a long distance to walk.", "Ten kilometre is a long distance to walk.", "Ten kilometres are long distance to walk."], "medium", "An amount of distance, money or time treated as one quantity takes a **singular** verb: *Ten kilometres **is** a long distance*."),
    ("sc-insisted-on", FILL, "He insisted ___ paying the bill.", ["on", "to", "for", "at"], "medium", "**Insist** takes *on* + *-ing*: *insisted on paying*."),
    # ---- hard
    ("sc-not-only-but-also", SPOT, "(A) Not only the students / (B) but also the teacher / (C) were invited to the event. / (D) No error", ["(C) were invited to the event.", "(A) Not only the students", "(B) but also the teacher", "(D) No error"], "hard", "With *not only … but also*, the verb agrees with the **nearer** subject — *the teacher* (singular) → *was invited*."),
    ("sc-had-i-known", CORRECT, "", ["Had I known about the delay, I would have taken another route.", "If I would have known about the delay, I would have taken another route.", "Had I knew about the delay, I would take another route.", "If I had known about the delay, I would take another route."], "hard", "A past unreal condition uses the past perfect in the *if*-clause (or the inverted *Had I known*) and *would have* + past participle in the result. *If I would have known* is incorrect."),
    ("sc-reason-is-that", CORRECT, "", ["The reason he failed is that he did not prepare.", "The reason he failed is because he did not prepare.", "The reason why he failed is because he did not prepare.", "The reason he failed was because of he did not prepare."], "hard", "**The reason … is that** — *because* repeats the idea of *reason*, so *the reason is because* is redundant."),
    ("sc-being-rainy", SPOT, "(A) Being a rainy day, / (B) we decided / (C) to stay indoors. / (D) No error", ["(A) Being a rainy day,", "(B) we decided", "(C) to stay indoors.", "(D) No error"], "hard", "A dangling participle: *Being a rainy day* seems to describe *we*. Correct: *It being a rainy day, we decided…* or *As it was a rainy day…*"),
    ("sc-not-until", CORRECT, "", ["Not until the results were announced did she relax.", "Not until the results were announced she relaxed.", "Not until the results announced did she relax.", "Not until were the results announced did she relax."], "hard", "A sentence starting with **Not until** inverts the *main* clause (*did she relax*); the *until*-clause keeps normal order."),
    ("sc-cost-is", SPOT, "(A) The cost of / (B) these new phones / (C) are rising every year. / (D) No error", ["(C) are rising every year.", "(A) The cost of", "(B) these new phones", "(D) No error"], "hard", "The subject is **cost** (singular), not *phones*: *The cost … **is** rising*."),
    ("sc-hardly-anyone", CORRECT, "", ["Hardly anyone attended the lecture.", "Hardly no one attended the lecture.", "Hardly anyone didn't attend the lecture.", "Hardly any one did not attended the lecture."], "hard", "**Hardly** is already negative, so it can't be combined with *no one* or *didn't* (double negative)."),
    ("sc-cannot-hardly", SPOT, "(A) He is so tired / (B) that he / (C) cannot hardly walk. / (D) No error", ["(C) cannot hardly walk.", "(A) He is so tired", "(B) that he", "(D) No error"], "hard", "*Cannot hardly* is a double negative. Correct: *he can hardly walk*."),
    ("sc-whom-invite", CORRECT, "", ["Whom did you invite to the party?", "Who did you invited to the party?", "Whom you did invite to the party?", "Whom did you invited to the party?"], "hard", "The pronoun is the object of *invite*, so formal English uses **whom**; after *did*, the verb is the base form (*invite*), and the question needs inversion (*did you*)."),
    ("sc-along-with", SPOT, "(A) The manager, along with his assistants, / (B) are attending / (C) the conference today. / (D) No error", ["(B) are attending", "(A) The manager, along with his assistants,", "(C) the conference today.", "(D) No error"], "hard", "Phrases like *along with*, *as well as* and *together with* don't change the subject: *The manager … **is** attending*."),
]


def _titles(slug, kind, prompt):
    if kind == SYN:
        return f"Synonym: {prompt.capitalize()}"
    if kind == ANT:
        return f"Antonym: {prompt.capitalize()}"
    if kind == OWS:
        return f"One word: {prompt[0].lower() + prompt[1:]}"
    if kind == IDIOM:
        return f"Idiom: {prompt}"
    if kind == FILL:
        return f"Fill in: {prompt}"
    if kind == SPOT:
        return "Spot the error: " + " ".join(part.split(") ", 1)[1].strip(" /") for part in prompt.split(" / ")[:-1])
    return "Correct sentence: " + slug.removeprefix("sc-").replace("-", " ")


def _build(entries):
    rng = random.Random("verbal-bank")
    out = []
    for slug, kind, prompt, options, difficulty, explanation in entries:
        correct = options[0]
        shuffled = options[:]
        rng.shuffle(shuffled)
        if kind == SPOT:  # keep the parts in A–D order
            shuffled = sorted(options, key=lambda o: o[:3])
        out.append({
            "slug": slug,
            "title": _titles(slug, kind, prompt),
            "type": "mcq",
            "difficulty": difficulty,
            "statement": kind.format(w=prompt) if "{w}" in kind else kind,
            "options": shuffled,
            "answer": ascii_uppercase[shuffled.index(correct)],
            "explanation": explanation,
        })
    return out


TOPICS = {
    "vocabulary": _build(VOCABULARY),
    "sentence-correction": _build(SENTENCE_CORRECTION),
}
