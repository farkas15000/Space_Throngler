import pygame
from pygame._sdl2.video import Renderer


class BVH(pygame.sprite.Sprite):

    def __init__(self, max_depth, sprites=(), rect=None, depth=1):
        # max_depth = max recursion level
        # sprites = List of objects with self.rect !

        pygame.sprite.Sprite.__init__(self)
        self.depth = depth
        count = len(sprites)
        if rect is None:
            if count:
                tlx = sprites[0].rect.x
                tly = sprites[0].rect.y
                brx = sprites[0].rect.right
                bry = sprites[0].rect.bottom
                for sprite in sprites:
                    rect = sprite.rect
                    if rect.x < tlx:
                        tlx = rect.x
                    if rect.y < tly:
                        tly = rect.y
                    if rect.right > brx:
                        brx = rect.right
                    if rect.bottom > bry:
                        bry = rect.bottom
                self.rect = pygame.rect.Rect(tlx, tly, brx-tlx, bry-tly)
            else:
                self.rect = pygame.rect.Rect(0, 0, 0, 0)
            hold = sprites
        else:
            hold = []
            self.rect = rect
            for sprite in sprites:
                if pygame.sprite.collide_rect(sprite, self):
                    hold.append(sprite)

        self.child = tuple()
        self.sprites = []

        if self.depth < max_depth and len(hold) > 2 and self.rect.w >= 8 and self.rect.h >= 8:
            w = self.rect.w % 2
            h = self.rect.h % 2

            if self.depth % 2 == 0:
                lelt = pygame.rect.Rect(self.rect.x, self.rect.y, self.rect.w // 2 + w, self.rect.h)
                right = pygame.rect.Rect(self.rect.x + self.rect.w // 2 + w, self.rect.y, self.rect.w // 2, self.rect.h)
                self.child = (BVH(max_depth=max_depth, sprites=hold, rect=lelt, depth=self.depth+1),
                              BVH(max_depth=max_depth, sprites=hold, rect=right, depth=self.depth+1))
            else:
                top = pygame.rect.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h//2+h)
                down = pygame.rect.Rect(self.rect.x, self.rect.y+self.rect.h//2+h, self.rect.w, self.rect.h//2+h)
                self.child = (BVH(max_depth=max_depth, sprites=hold, rect=top, depth=self.depth + 1),
                              BVH(max_depth=max_depth, sprites=hold, rect=down, depth=self.depth + 1))
        else:
            self.sprites = hold

    def collisionSet(self, hit_set=None):
        # returns a set with non-repeating collides object pairs in tuples

        if hit_set is None:
            hit_set = set()
        if not self.sprites:
            for child in self.child:
                child.collisionSet(hit_set)
        else:
            for x, item1 in enumerate(self.sprites):
                for item2 in self.sprites[x + 1:]:
                    if (item1, item2) not in hit_set and pygame.sprite.collide_rect(item1, item2):
                        hit_set.add((item1, item2))
        return hit_set

    def collisionDict(self, hit_dict=None):
        # returns a dict where the keys are all the objects that had collisions and the values are all the collided objects in a set
        # probably slower than collisionSet but easier to use

        if hit_dict is None:
            hit_dict = dict()
        if not self.sprites:
            for child in self.child:
                child.collisionDict(hit_dict)
        else:
            for x, item1 in enumerate(self.sprites):
                for item2 in self.sprites[x + 1:]:
                    if pygame.sprite.collide_rect(item1, item2):

                        if item1 not in hit_dict:
                            hit_dict[item1] = set()
                        hit_dict[item1].add(item2)

                        if item2 not in hit_dict:
                            hit_dict[item2] = set()
                        hit_dict[item2].add(item1)

        return hit_dict

    def collisionRect(self, rect, hit_set=None, draw=None):
        # returns a set of all the collided objects with the given rect
        # debug draw shows the hit tree nodes. needs render surface

        if hit_set is None:
            hit_set = set()

        if self.rect.colliderect(rect):
            if not self.sprites:
                for child in self.child:
                    child.collisionRect(rect, hit_set, draw=draw)
            else:
                for item1 in self.sprites:
                    if rect.colliderect(item1.rect):
                        hit_set.add(item1)
            if draw:
                self.root(draw)

        return hit_set

    def draw(self, renderer: Renderer):
        # draws the whole tree
        renderer.draw_color = (0, 0, 255, 0)
        renderer.draw_rect(self.rect)
        for child in self.child:
            child.draw(renderer)
        for item in self.sprites:
            renderer.draw_color = (255, 0, 0, 0)
            renderer.draw_rect(item.rect)

    def root(self, renderer):
        # draws the root of the tree
        renderer.draw_color = (255, 0, 0, 0)
        renderer.draw_rect(self.rect)

    def info(self):
        # debug everything
        print(self.depth, self.rect, "items:")
        for item in self.sprites:
            print(type(item), item.rect)
        for children in self.child:
            children.info()


class Collider:
    # dummy object for BVH

    def __init__(self, abs_rect):
        self.rect = abs_rect

    def collision(self, hits):
        pass
