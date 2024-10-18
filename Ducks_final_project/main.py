import math
import sweeperlib
import random

WIN_WIDTH = 1400
WIN_HEIGHT = 800
GRAVITATIONAL_ACCEL = 1.1

game = {
    "x": 40,
    "y": 40,
    "w": 40,
    "h": 40,
    "angle": 0,
    "force": 0,
    "x_velocity": 0,
    "y_velocity": 0,
    "ducks_left": 10,
    "flight": False,
    "gamemenu": True,
    "draw_dots": True,
    "target": -1,
    "xm": 0,
    "ym": 0,
    "gameflight": True,
    "random": False  
}

map_names = {
    "map1": "map1.txt",
    "map2": "None", 
    "map3": "None"
}

levels_info = {
    "level1": True,
    "level2": False,
    "level3": False,
    "levels": False
}

level = 1
map_number = 1
obstacles = []
targets = []
ob_collision = False
target_collision = False
mapfile = "map1.txt"


def load_map(map_file):
    """
    This function is called then the user choose the levels game. 
    It read a file of the map and write it in the dictianare.
    """
    global obstacles, targets, map_number
    obstacles = []
    targets = []
    game["target"] = 0

    with open(map_file, 'r') as file:
        for line in file:
            parts = line.split()
            if parts[0].startswith('obstacle'):
                obstacles.append({
                    "obstacletype": str(parts[0]),
                    "x": int(parts[1]),
                    "y": int(parts[2]),
                    "w": int(parts[3]),
                    "h": int(parts[4]),
                })
            elif parts[0].startswith("target"):
                targets.append({
                    "targetname": str(parts[0]),
                    "x": int(parts[1]),
                    "y": int(parts[2]),
                    "w": int(parts[3]),
                    "h": int(parts[4]),
                })
            elif parts[0] == 'lives':
                game["ducks_left"] = int(parts[1])
            elif parts[0] == "nextmap" and levels_info["levels"]:
                map_names[f"map{map_number}"] = parts[1]
                print(map_names)


def create_random_map():
    """
    This function is called then the user want to play a random mode. 
    This function randomas the values of the object and 
    also make sure that the objects not gonna overlape on each other.
    """
    global obstacles, targets, level, map_number
    obstacles = []
    targets = []
    game["target"] = 0

    def check_collision2(x, y, w, h, objects):
        for object in objects:
            if (
                x < object["x"] + object["w"]
                and x + w > object["x"]
                and y < object["y"] + object["h"]
                and y + h > object["y"]
            ):
                return True
        return False

    for i in range(random.randrange(1, 7)):
        obstacle = {
            "obstacletype": f"obstacle{random.randrange(1, 4)}",
            "x": random.randrange(150, WIN_WIDTH - 150),
            "y": random.randrange(150, WIN_HEIGHT - 200),
            "w": 120,
            "h": 120,
            "vy": 0,
        }
        while check_collision2(obstacle["x"], obstacle["y"], obstacle["w"], obstacle["h"], obstacles):
            obstacle["x"] = random.randrange(150, WIN_WIDTH - 40)
            obstacle["y"] = random.randrange(150, WIN_HEIGHT - 200)
        obstacles.append(obstacle)

    for i in range(random.randrange(1, 7)):
        target = {
            "targetname": f"target{random.randrange(1, 4)}",
            "x": random.randrange(150, WIN_WIDTH - 40),
            "y": random.randrange(150, WIN_HEIGHT - 200),
            "w": 40,
            "h": 40,
            "vy": 0,
        }

        while check_collision2(target["x"], target["y"], target["w"], target["h"], targets):
            target["x"] = random.randrange(150, WIN_WIDTH - 40)
            target["y"] = random.randrange(150, WIN_HEIGHT - 200)
        targets.append(target)

    game["ducks_left"] = random.randrange(len(targets), 10)


def initialize_game():
    """ this function is called then the game need to be initialize 
    for example then duck hit a obstical 
    """
    global ob_collision, target_collision
    game["x"] = 40
    game["y"] = 40
    game["x_velocity"] = 0
    game["y_velocity"] = 0
    game["flight"] = False
    game["draw_dots"] = True
    ob_collision = False
    target_collision = False


def launch():
    """ This function is launch duck each time 
    the user drag the mouse and then relise it
    """
    angle_radians = math.radians(game["angle"])
    game["x_velocity"] = game["force"] * math.cos(angle_radians)
    game["y_velocity"] = game["force"] * math.sin(angle_radians)
    game["flight"] = True
    game["draw_dots"] = False


def flight(elapsed):
    """ This function is cange the status of the game during flight, 
    all the collision, change in velocity and indicate then game is oveer. 
    This function is working after launch until the user is lose or win.
    """
    global ob_collision, target_collision, level, mapfile, map_number
    result = False
    if game["flight"]:
        game["x"] += game["x_velocity"]
        game["y"] += game["y_velocity"]
        game["y_velocity"] -= GRAVITATIONAL_ACCEL
        for obstacle in obstacles:
            if check_collision(game, obstacle):
                result = True
        if game["y"] <= 0 or game["x"] > WIN_WIDTH or result:
            ob_collision = True
            game["ducks_left"] -= 1
            initialize_game()
        if game["ducks_left"] == 0:
            game["xm"] = 0
            game["ym"] = 0
            game["gameflight"] = False
            if game["random"]:
                game["random"] = False
                levels_info["levels"] = True
            sweeperlib.set_draw_handler(draw)
        if check_collision(game, targets):
            if len(targets) == 0: 
                if game["random"]:
                    create_random_map()
                    initialize_game()
                else:
                    game["xm"] = 0
                    game["ym"] = 0
                    map_number +=1
                    levels_info[f"level{map_number}"] = True
                    levels_info["levels"] = True
                    game["gameflight"] = False
                    sweeperlib.set_draw_handler(draw)



def check_collision(object1, object2):
    """ This function called then the collision need to be checked"""
    if not game["flight"]:
        return False

    if isinstance(object2, list):
        for target in object2:
            if (
                object1["x"] < target["x"] + target["w"]
                and object1["x"] + object1["w"] > target["x"]
                and object1["y"] < target["y"] + target["h"]
                and object1["y"] + object1["h"] > target["y"]
            ):
                game["target"] -= 1
                object2.remove(target) 
                return True
    elif isinstance(object2, dict):
        return (
            object1["x"] < object2["x"] + object2["w"]
            and object1["x"] + object1["w"] > object2["x"]
            and object1["y"] < object2["y"] + object2["h"]
            and object1["y"] + object1["h"] > object2["y"]
        )

    return False


def draw():
    """Draw all the maps and the menu, and in general sprites"""
    global mapfile
    if game["gamemenu"]:
        game["flight"] = False
        sweeperlib.clear_window()
        sweeperlib.begin_sprite_draw()
        sweeperlib.prepare_sprite("menu", 0, 0)
        sweeperlib.draw_sprites()
        if 450 <= game["xm"] <= 950 and 500 <= game["ym"] <= 580:
            game["gamemenu"] = False
            levels_info["levels"] = True
            print("hi")
            game["xm"] = 0
            game["ym"] = 0
        if 450 <= game["xm"] <= 950 and 300 <= game["ym"] <= 380:
            game["gamemenu"] = False
            game["random"] = True
            game["xm"] = 0
            game["ym"] = 0
            create_random_map()
    elif levels_info["levels"]:
        game["gameflight"] = False
        sweeperlib.clear_window()
        sweeperlib.begin_sprite_draw()
        sweeperlib.prepare_sprite("background", 0, 0)
        for i in range(3):
            if levels_info[f"level{i+1}"] == True :
                sweeperlib.prepare_sprite(f"menu{i+1}", 200 + i*400, 400)
            else:
                sweeperlib.prepare_sprite(f"grey{i+1}", 200 + i*400, 400)
        sweeperlib.draw_sprites()
        for i in range(3):
            if 400 < game["ym"] < 600 and 200 + i*400 < game["xm"] < 400 + i*400 and levels_info[f"level{i+1}"]:
                game["ym"] = 0
                game["xm"] = 0
                load_map(f"map{i+1}.txt")
                mapfile = (f"map{i+1}.txt")
                initialize_game()
                levels_info["levels"] = False
                game["gameflight"] = True

    elif not game["gamemenu"] and not levels_info["levels"] and game["ducks_left"] > 0:
        sweeperlib.clear_window()
        sweeperlib.draw_background()
        sweeperlib.begin_sprite_draw()
        sweeperlib.prepare_sprite("background", 0, 0)
        sweeperlib.draw_sprites()
        sweeperlib.prepare_sprite("sling", 100, 20)
        sweeperlib.prepare_sprite("duck", game["x"], game["y"])

        for obstacle in obstacles:
            sweeperlib.prepare_sprite(obstacle["obstacletype"], obstacle["x"], obstacle["y"])

        for target in targets:
            sweeperlib.prepare_sprite(target["targetname"], target["x"], target["y"])

        sweeperlib.draw_sprites()
        sweeperlib.draw_text("{}°\tforce: {}".format(game["angle"], game["force"]), 10, 680)
        for i in range(game['ducks_left']):
            sweeperlib.prepare_sprite("lives", 10+i*60, 740)
            sweeperlib.draw_sprites()
        if game["draw_dots"]:
            for i in range(3, 10):
                angle_radians = math.radians(game["angle"])
                sweeperlib.prepare_sprite("dot", (game["force"] * math.cos(angle_radians)*i+((i**2)/2)),
                                           game["force"] * math.sin(angle_radians)*i)
                sweeperlib.draw_sprites()
    elif game["ducks_left"] == 0 and not game["gameflight"]:
        sweeperlib.clear_window()
        sweeperlib.begin_sprite_draw()
        sweeperlib.prepare_sprite("background", 0, 0)
        sweeperlib.prepare_sprite("tryagain", 400, 300)
        sweeperlib.prepare_sprite("lose", 450, 600)
        sweeperlib.draw_sprites()
        if 300 < game["ym"] < 500 and 500 < game["xm"] < 900:
            print("hello")
            initialize_game()  # Reset game state
            load_map(mapfile)  # Reload the current map
            game["gameflight"] = True
        sweeperlib.draw_sprites()


def mouse_drag_handler(x, y, dx, dy, buttons, modifiers):
    """ mouse drag handler"""
    normalized_x = x / WIN_WIDTH
    normalized_y = y / WIN_HEIGHT
    game["xm"] = x
    game["ym"] = y

    if buttons & sweeperlib.MOUSE_LEFT:
        game["angle"] = math.degrees(math.acos(normalized_x / math.sqrt(normalized_x**2 + normalized_y**2)))
        game["force"] = 70 * math.sqrt(normalized_x**2 + normalized_y**2)


def mouse_release_handler(x, y, button, modifiers):
    """Mouse release handler"""
    game["xm"] = x
    game["ym"] = y
    if button == sweeperlib.MOUSE_LEFT and game["gamemenu"] == False:
        launch()


if __name__ == "__main__":
    sweeperlib.load_sprites("sprites")
    sweeperlib.create_window(width=WIN_WIDTH, height=WIN_HEIGHT)
    sweeperlib.set_draw_handler(draw)
    sweeperlib.set_drag_handler(mouse_drag_handler)
    sweeperlib.set_release_handler(mouse_release_handler)
    sweeperlib.set_interval_handler(flight)

    sweeperlib.start()

