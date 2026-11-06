
def notify(kind, email, title="", send=True):
    if not send:
        return

    if kind == "checkout":
        subject = "Book checked out"
        body = "You checked out " + title

    elif kind == "renew":
        subject = "Loan renewed"
        body = "You renewed " + title

    else:
        subject = "Library notice"
        body = title

    with open("outbox.txt", "a") as file:
        file.write(
            "TO: " + email
            + " | SUBJECT: " + subject
            + " | BODY: " + body + "\n"
        )
