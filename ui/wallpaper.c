#include "wallpaper.h"
#include <string.h>

static lv_image_dsc_t dsc;
static bool have;

uint32_t wallpaper_hash(const void *p, size_t n)
{
    const uint8_t *b = p;
    uint32_t h = 2166136261u;
    for (size_t i = 0; i < n; i++) h = (h ^ b[i]) * 16777619u;
    return h;
}

void wallpaper_use(const uint16_t *px, int w, int h)
{
    memset(&dsc, 0, sizeof dsc);
    dsc.header.magic = LV_IMAGE_HEADER_MAGIC;
    dsc.header.cf = LV_COLOR_FORMAT_RGB565;
    dsc.header.w = (uint32_t)w;
    dsc.header.h = (uint32_t)h;
    dsc.header.stride = (uint32_t)w * 2;
    dsc.data_size = (uint32_t)w * (uint32_t)h * 2;
    dsc.data = (const uint8_t *)px;
    have = true;
}

const lv_image_dsc_t *wallpaper_get(void) { return have ? &dsc : NULL; }
