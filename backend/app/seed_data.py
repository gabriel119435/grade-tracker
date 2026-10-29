# demo content for routes/seed.py

# 10 male + 10 female first names, 20 last names, pt-br spelling
FIRST_NAMES = [
    # male
    "josé",
    "joão",
    "antônio",
    "francisco",
    "pedro",
    "carlos",
    "lucas",
    "luiz",
    "paulo",
    "gabriel",
    # female
    "maria",
    "ana",
    "francisca",
    "júlia",
    "antônia",
    "juliana",
    "adriana",
    "fernanda",
    "márcia",
    "patrícia",
]
LAST_NAMES = [
    "silva",
    "santos",
    "oliveira",
    "souza",
    "pereira",
    "ferreira",
    "lima",
    "alves",
    "rodrigues",
    "costa",
    "sousa",
    "gomes",
    "nascimento",
    "araújo",
    "ribeiro",
    "almeida",
    "jesus",
    "barbosa",
    "soares",
    "carvalho",
]

CATEGORIES = {
    "saque": ["chapado", "chapado lob", "top spin", "top spin lob", "por baixo", "swing volley"],
    "recepção": ["alta de forehand", "baixa de forehand", "alta de backhand", "baixa de backhand", "split step"],
    "forehand": ["acelerada", "swing volley", "peixinho", "anômalo", "defesa alta", "defesa baixa"],
    "backhand": ["acelerada", "swing volley", "peixinho", "defesa alta", "defesa baixa"],
    "voleio": [
        "alto de forehand",
        "alto de forehand top spin",
        "alto de backhand",
        "baixo de forehand",
        "baixo de backhand",
        "bloqueio",
    ],
    "smash": ["smash", "smash drop", "smash lob"],
    "lob": [
        "voleio alto de forehand",
        "voleio alto de backhand",
        "voleio baixo de forehand",
        "voleio baixo de backhand",
    ],
    "gancho": ["gancho", "gancho lob", "gancho drop"],
    "verônica": ["verônica", "verônica lob"],
    "curta": ["de forehand", "de backhand", "voleio alto de forehand", "voleio alto de backhand"],
}
