import os
import pygame
import settings
from threading import Thread
from ui import GenericList, AnimatedImage
from util_functs import Utils


class PerksTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.perks_font = pygame.font.Font(settings.ROBOTO_CONDENSED_PATH, 12)
        self.description_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9)
        
        list_draw_space = pygame.Rect(
            self.draw_space.left,
            self.draw_space.top + 2 * settings.LIST_TOP_MARGIN,
            self.draw_space.centerx - 2 * settings.TAB_SIDE_MARGIN,
            self.draw_space.height - 2 * settings.LIST_TOP_MARGIN
        )
        
        # Liste des perks (noms affichés)
        self.perks_list = GenericList(
            draw_space=list_draw_space,
            items=settings.PERKS,  # À définir dans settings.py
            font=self.perks_font
        )
        
        self.selected_perk_index = 0
        self.previous_perk_index = 0
        
        self.perk_text = self._init_perk_text()
        
        self.animated_images = {}
        self.current_loaded_perk = None
        self.perk_images_cache = {}  # Cache pour les images déjà chargées
        self.frame_orders_cache = {}  # Cache pour les frame orders
    
    def handle_threads(self, tab_selected: bool):
        """Handle the threads - STOP immédiat si déselectionné"""
        
        # LOG dans un fichier
        with open("/tmp/perks_debug.log", "a") as f:
            f.write(f"handle_threads called: {tab_selected}\n")

        if not tab_selected:
            # ARRÊT BRUTAL DE TOUS LES SONS
            pygame.mixer.stop()
            # Arrêter toutes les animations
            for anim in list(self.animated_images.values()):
                anim.stop()
            return
    
        # Démarrage normal
        perk = settings.PERKS[self.selected_perk_index]
        self._load_perk_animation(perk)
    
        if perk in self.animated_images:
            self.animated_images[perk].start()
    
    def _load_perk_animation(self, perk):
        """Charge l'animation d'un perk à la demande"""
        if perk in self.animated_images:
            return  # Déjà chargé
    
        perk_folder = perk.lower().replace(" ", "_")
    
        # Charger les images si pas encore en cache
        if perk_folder not in self.perk_images_cache:
            path = f"{settings.PERKS_BASE_FOLDER}/{perk_folder}"
        
            if not os.path.exists(path):
                return
        
            images = []
            for file in sorted(os.listdir(path)):
                if file.endswith(".png"):
                    images.append(
                        Utils.scale_image(
                            Utils.tint_image(
                                pygame.image.load(os.path.join(path, file)).convert_alpha()
                            ),
                            0.70
                        )
                    )
        
            # Charger frame order
            if os.path.exists(os.path.join(path, "frameorder.ini")):
                with open(os.path.join(path, "frameorder.ini"), "r") as f:
                    frame_order = [int(frame) for frame in (f.read().split(","))]
            else:
                frame_order = list(range(0, len(images)))
        
            self.perk_images_cache[perk_folder] = images
            self.frame_orders_cache[perk_folder] = frame_order
    
        # Créer l'AnimatedImage
        if not self.perk_images_cache[perk_folder]:
            return
    
        image_width = self.perk_images_cache[perk_folder][0].get_width()
    
        self.animated_images[perk] = AnimatedImage(
            self.screen,
            self.perk_images_cache[perk_folder],
            (self.draw_space.centerx + self.draw_space.width // 4 - image_width // 2,
             self.draw_space.top + settings.LIST_TOP_MARGIN),
            settings.SPEED * 200,
            self.frame_orders_cache[perk_folder],
            loop=True,
            sound_path=f"{settings.PERK_SOUNDS}/{perk_folder}.ogg" if not settings.GAME_ACCURATE_MODE else None
        )



    def scroll(self, direction: bool):
        """Scroll through perks and restart animation if needed."""
        prev_index = self.perks_list.change_selection(direction)
        selected_index = self.perks_list.selected_index
        
        if selected_index != prev_index:
            # Stop previous animation
            prev_perk = settings.PERKS[prev_index]
            if prev_perk in self.animated_images:
                self.animated_images[prev_perk].stop()
            
            # Start new animation
            self.selected_perk_index = selected_index
            current_perk = settings.PERKS[self.selected_perk_index]
            self._load_perk_animation(current_perk)

            if current_perk in self.animated_images:
                self.animated_images[current_perk].reset()
                self.animated_images[current_perk].start()
    
    def _init_perk_text(self):
        perk_descriptions = {}
        
        for description in settings.PERK_DESCRIPTIONS:
            text = self.description_font.render(description, True, settings.PIP_BOY_LIGHT, wraplength=self.draw_space.centerx)
            surface = pygame.surface.Surface((self.draw_space.centerx, text.get_height()))
            surface.blit(text, (0, 0))
            
            perk_descriptions[description.split(" ")[0]] = surface
        
        return perk_descriptions
    
    def _render_perk_images(self, selected_perk):
        """Render animation safely."""
        if selected_perk in self.animated_images:
            self.animated_images[selected_perk].render()
    
    def _render_perk_text(self, selected_perk):
        perk_key = selected_perk.split(" ")[0]
        if perk_key in self.perk_text:
            self.screen.blit(
                self.perk_text[perk_key],
                (self.draw_space.centerx, self.draw_space.centery + (self.draw_space.centery // 4))
            )
    
    def render(self):
        """Render the entire tab UI."""
        if not self.perks_list:
            return
        
        selected_perk = settings.PERKS[self.selected_perk_index]
        self.perks_list.render(self.screen)
        self._render_perk_images(selected_perk)
        self._render_perk_text(selected_perk)
