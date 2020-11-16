class Map:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.map = (width * height) * [-1]

    def index(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height: return -1
        return x + y * self.width

    def get(self, x, y):
        i = self.index(x, y)
        if i < 0: return -1
        return self.map[i]

    def set(self, x, y, value):
        i = self.index(x, y)
        if i < 0: return -1
        self.map[i] = value
        return value


from math import cos, sin


class Raycaster:
    def __init__(self, map_get):
        self.map_get = map_get     # Map->get.
        self.walls_distance = 10   # Where to stop looking for walls.
        self.screen_width = 10     # Screen resolution.

    def cast(self, pos, rot):
        pos_x = int(pos[0])
        pos_y = int(pos[1])
        # Rotation vector.
        rot_x = cos(rot)
        rot_y = sin(rot)
        # Direction vector.
        dir_x = -rot_x
        dir_y = -rot_y
        # The 2d raycaster version of camera plane.
        plane_x = -0.66 * rot_y # Why 0.66? idono.
        plane_y = +0.66 * rot_x
        # Casts ray.
        for x in range(self.screen_width):
            # x-coordinate in camera space.
            camera_x = 2 * x / self.screen_width - 1
            # Ray position and direction.
            ray_dir_x = dir_x + plane_x * camera_x
            ray_dir_y = dir_y + plane_y * camera_x
            # Length of ray from one x or y-side to next x or y-side.
            delta_x = abs(1 / ray_dir_x)
            delta_y = abs(1 / ray_dir_y)
            # Which box of the map we're in.
            map_x = pos_x
            map_y = pos_y
            # Length of ray from current position to next x or y-side.
            side_dist_x = 0
            side_dist_y = 0
            # What direction to step in x or y-direction (either +1 or -1).
            step_x = 0
            step_y = 0       #
            # Calculating step and initial side_dist.
            # -0.5 do eyes coordinates be centered.
            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = -delta_x * (    map_x - pos_x - 0.5)
            else:
                step_x = +1
                side_dist_x = +delta_x * (1 + map_x - pos_x - 0.5)
            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = -delta_y * (    map_y - pos_y - 0.5)
            else:
                step_y = +1
                side_dist_y = +delta_y * (1 + map_y - pos_y - 0.5)
            # Performing DDA.
            side = 0  # Was a NS or a EW wall hit?
            for INF in range(self.walls_distance):
                # Jump to next map square, OR in x-direction, OR in y-direction.
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_y
                    map_y += step_y
                    side = 1
                # Check if ray has hit a wall.
                hit = self.map_get(map_x, map_y)
                if hit >= 0:
                    dist = ((map_x - pos_x) **2 + (map_y - pos_y) **2) **0.5
                    # TODO: Saves data (hit and dist)
                    break
        return None
