import turtle

def show_intro( show = True, duration = 2.0 ):
    if not show:
        return
    
    screen = turtle.Screen()
    screen.setup(800, 600)
    screen.title("Space Invaders Game Intro")
    screen.bgcolor("black")

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



