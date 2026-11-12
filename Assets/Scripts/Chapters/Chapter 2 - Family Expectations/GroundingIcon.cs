using UnityEngine;
using UnityEngine.UIElements;

namespace Mindscape.FamilyExpectations
{
    // Small coloured vector pictures of things in the examination room, for the 5-4-3-2-1 grounding break: the player
    // taps the pictures instead of only reading a list. Drawn with Painter2D so they need no textures and stay crisp.
    // Kind: desk, paper, pencil, window, clock, chair, feet, water, fan, board, breath, sleeves.
    public sealed class GroundingIcon : VisualElement
    {
        readonly string kind;

        public GroundingIcon(string kind) { this.kind = kind; pickingMode = PickingMode.Ignore; generateVisualContent += Draw; }

        static readonly Color Ink = new Color(.17f, .16f, .14f), Wood = new Color(.62f, .43f, .27f), DarkWood = new Color(.45f, .3f, .18f),
            Cream = new Color(.98f, .96f, .9f), Sky = new Color(.55f, .78f, .93f), Water = new Color(.62f, .83f, .96f),
            Yellow = new Color(.98f, .78f, .25f), Pink = new Color(.93f, .55f, .6f), Green = new Color(.23f, .42f, .33f),
            Grey = new Color(.6f, .6f, .62f), Navy = new Color(.16f, .24f, .45f);

        void Draw(MeshGenerationContext ctx)
        {
            float w = contentRect.width, h = contentRect.height;
            if (w <= 0 || h <= 0) return;
            float s = Mathf.Min(w, h), ox = (w - s) * .5f, oy = (h - s) * .5f;
            var p = ctx.painter2D;
            p.lineJoin = LineJoin.Round; p.lineCap = LineCap.Round;
            Vector2 V(float x, float y) => new Vector2(ox + x * s, oy + y * s);
            void Poly(Color fill, params float[] c)
            {
                p.BeginPath(); p.MoveTo(V(c[0], c[1]));
                for (int i = 2; i < c.Length; i += 2) p.LineTo(V(c[i], c[i + 1]));
                p.ClosePath(); p.fillColor = fill; p.Fill();
                p.strokeColor = Ink; p.lineWidth = Mathf.Max(1, s * .025f); p.Stroke();
            }
            void Rect(Color fill, float x0, float y0, float x1, float y1) => Poly(fill, x0, y0, x1, y0, x1, y1, x0, y1);
            void Disc(Color fill, float x, float y, float r, bool outline = true)
            {
                p.BeginPath(); p.Arc(V(x, y), r * s, 0, 360); p.ClosePath(); p.fillColor = fill; p.Fill();
                if (outline) { p.strokeColor = Ink; p.lineWidth = Mathf.Max(1, s * .025f); p.Stroke(); }
            }
            void Line(Color c, float width, params float[] pts)
            {
                p.BeginPath(); p.MoveTo(V(pts[0], pts[1]));
                for (int i = 2; i < pts.Length; i += 2) p.LineTo(V(pts[i], pts[i + 1]));
                p.strokeColor = c; p.lineWidth = Mathf.Max(1, s * width); p.Stroke();
            }

            switch (kind)
            {
                case "desk":
                    Rect(Wood, .14f, .47f, .22f, .9f); Rect(Wood, .78f, .47f, .86f, .9f);
                    Rect(DarkWood, .5f, .47f, .76f, .63f); Disc(Ink, .63f, .55f, .02f, false);
                    Rect(Wood, .06f, .36f, .94f, .48f);
                    break;
                case "paper":
                    Poly(Cream, .22f, .08f, .66f, .08f, .78f, .2f, .78f, .92f, .22f, .92f);
                    for (float y = .32f; y < .82f; y += .12f) Line(Grey, .02f, .32f, y, .68f, y);
                    Line(Navy, .035f, .32f, .2f, .5f, .2f);
                    break;
                case "pencil":
                    Poly(Yellow, .14f, .76f, .62f, .28f, .72f, .38f, .24f, .86f);
                    Poly(new Color(.93f, .8f, .62f), .62f, .28f, .86f, .14f, .72f, .38f);
                    Disc(Ink, .82f, .17f, .025f, false);
                    Poly(Pink, .14f, .76f, .24f, .86f, .16f, .94f, .06f, .84f);
                    break;
                case "window":
                    Rect(Sky, .16f, .12f, .84f, .86f);
                    Disc(Cream, .34f, .34f, .07f, false); Disc(Cream, .42f, .32f, .08f, false);
                    Line(Cream, .06f, .5f, .12f, .5f, .86f); Line(Cream, .06f, .16f, .49f, .84f, .49f);
                    Rect(Wood, .1f, .86f, .9f, .93f);
                    break;
                case "clock":
                    Disc(Cream, .5f, .5f, .38f);
                    for (int i = 0; i < 12; i++)
                    {
                        float a = i * Mathf.PI / 6, r0 = i % 3 == 0 ? .28f : .31f;
                        Line(Ink, .02f, .5f + Mathf.Cos(a) * r0, .5f + Mathf.Sin(a) * r0, .5f + Mathf.Cos(a) * .34f, .5f + Mathf.Sin(a) * .34f);
                    }
                    Line(Ink, .045f, .5f, .5f, .5f, .3f); Line(Ink, .035f, .5f, .5f, .66f, .58f); Disc(Pink, .5f, .5f, .035f, false);
                    break;
                case "chair":
                    Rect(Wood, .3f, .08f, .7f, .46f); Rect(DarkWood, .3f, .46f, .36f, .92f); Rect(DarkWood, .64f, .46f, .7f, .92f);
                    Rect(Wood, .22f, .5f, .78f, .6f); Rect(DarkWood, .24f, .6f, .3f, .92f); Rect(DarkWood, .7f, .6f, .76f, .92f);
                    break;
                case "feet":
                    Rect(new Color(.8f, .72f, .6f), .04f, .8f, .96f, .92f);
                    Poly(Ink, .14f, .8f, .14f, .58f, .3f, .58f, .3f, .68f, .46f, .72f, .46f, .8f);
                    Poly(Ink, .54f, .8f, .54f, .58f, .7f, .58f, .7f, .68f, .86f, .72f, .86f, .8f);
                    Rect(Navy, .16f, .3f, .28f, .58f); Rect(Navy, .56f, .3f, .68f, .58f);
                    break;
                case "water":
                    Rect(Navy, .41f, .07f, .59f, .17f); Rect(Water, .44f, .17f, .56f, .28f);
                    Poly(Water, .34f, .34f, .44f, .28f, .56f, .28f, .66f, .34f, .66f, .92f, .34f, .92f);
                    Rect(new Color(.4f, .66f, .9f), .34f, .5f, .66f, .92f);
                    Line(Cream, .03f, .4f, .58f, .4f, .82f);
                    break;
                case "fan":
                    for (int i = 0; i < 3; i++)
                    {
                        float a = i * Mathf.PI * 2 / 3 - Mathf.PI / 2, b = a + .55f;
                        Poly(new Color(.85f, .88f, .9f), .5f, .5f, .5f + Mathf.Cos(a) * .4f, .5f + Mathf.Sin(a) * .4f, .5f + Mathf.Cos(b) * .38f, .5f + Mathf.Sin(b) * .38f);
                    }
                    Disc(Grey, .5f, .5f, .09f);
                    Line(new Color(.55f, .75f, .9f), .03f, .08f, .2f, .18f, .16f); Line(new Color(.55f, .75f, .9f), .03f, .82f, .84f, .92f, .8f);
                    break;
                case "board":
                    Rect(Wood, .04f, .14f, .96f, .78f); Rect(Green, .09f, .19f, .91f, .73f);
                    Line(Cream, .03f, .18f, .34f, .5f, .34f); Line(Cream, .03f, .18f, .48f, .74f, .48f); Line(Cream, .03f, .18f, .6f, .4f, .6f);
                    Rect(Wood, .3f, .78f, .7f, .84f); Rect(Cream, .36f, .76f, .46f, .8f);
                    break;
                case "breath":
                    for (int i = 0; i < 3; i++)
                    {
                        float y = .3f + i * .2f;
                        p.BeginPath(); p.MoveTo(V(.1f, y));
                        p.BezierCurveTo(V(.3f, y - .12f), V(.45f, y + .12f), V(.62f, y));
                        p.BezierCurveTo(V(.72f, y - .08f), V(.86f, y - .06f), V(.84f, y + .06f));
                        p.strokeColor = new Color(.45f, .7f, .9f); p.lineWidth = s * .055f; p.Stroke();
                    }
                    break;
                case "sleeves":
                    Poly(Cream, .3f, .12f, .42f, .12f, .5f, .2f, .58f, .12f, .7f, .12f, .94f, .3f, .84f, .46f, .74f, .4f, .74f, .9f, .26f, .9f, .26f, .4f, .16f, .46f, .06f, .3f);
                    Line(Grey, .02f, .5f, .2f, .5f, .9f);
                    break;
                default:
                    Disc(Cream, .5f, .5f, .3f);
                    break;
            }
        }
    }
}
