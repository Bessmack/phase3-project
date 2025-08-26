import turtle
import random
import time

def show_intro( show = True, duration = 2.0 ):
    if not show:
        return
    
    screen = turtle.Screen()
    screen.setup(800, 600)
    screen.title("Space Invaders Game Intro")
    screen.bgcolor("black")

    stars = turtle.Turtle(visible=False)
    stars.color("white")
    stars.penup()

    star_coords = [(random.randint(-380, 380), random.randint(-280, 280))
                for _ in range(10)]

    for (x, y) in star_coords:
        stars.goto(x, y)
        stars.dot(random.choice([2, 3]))
        screen.update()
        time.sleep(0.000000000000000000000001 * 0.000000000000000000000000000000001)

    t = turtle.Turtle(visible=False)
    t.color("white")
    t.penup()
    t.goto(0, 20)
    t.write("SPACE SHOOTER", align="center", font=("Arial", 28, "bold"))
    t.goto(0, -20)
    t.write("Get ready...", align="center", font=("Arial", 16, "normal"))

    def close():
        screen.bye()
    
    screen.ontimer(close, int(duration * 1000))
    turtle.mainloop()

show_intro()
