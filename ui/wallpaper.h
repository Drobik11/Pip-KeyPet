/* A photo for the background of the menu and the apps (Pip's own screen stays black: his face is an opaque canvas).
   The panel / tools/wallpaper.py write it into the "storage" partition at WALL_AT; main.c reads it into PSRAM at boot
   and hands it over here; th_screen() puts it behind every screen. No file: nothing changes. */
#pragma once
#include "lvgl.h"
#include <stddef.h>
#include <stdint.h>

#define WALL_SIZE 466         /* the glass: pixels each way */
#define WALL_MAGIC "PWL1"
#define WALL_AT 0x100000      /* offset inside "storage": the mood history has the first 24 KB, the battery log 64..80 KB */

/* The flash image: this header, then w*h RGB565 pixels, little endian (LV_COLOR_FORMAT_RGB565 as it sits in memory). */
typedef struct {
    char magic[4];    /* WALL_MAGIC */
    uint16_t w, h;
    uint32_t bytes;   /* w * h * 2 */
    uint32_t check;   /* wallpaper_hash() of the pixels */
} wall_head_t;
_Static_assert(sizeof(wall_head_t) == 16, "the flash image header");

uint32_t wallpaper_hash(const void *p, size_t n); /* FNV-1a, 32 bit: tools/wallpaper.py and docs/wallpaper.html compute the same */
void wallpaper_use(const uint16_t *px, int w, int h); /* px stays valid for good (PSRAM, never freed) */
const lv_image_dsc_t *wallpaper_get(void);            /* NULL: no wallpaper */
