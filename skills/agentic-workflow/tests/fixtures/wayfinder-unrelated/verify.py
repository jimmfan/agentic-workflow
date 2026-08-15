from app import greeting


if greeting() != "hello, world!":
    raise SystemExit("greeting is not complete")
