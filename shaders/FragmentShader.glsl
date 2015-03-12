#version 330

smooth in vec4 interpColor;

out vec4 outputColor;

void main()
{
	// TODO: Ideally color should be calculated in the fragment shader to avoid Interpolation
	// http://www.arcsynthesis.org/gltut/Illumination/Tut10%20Interpolation.html

	outputColor = interpColor;
}