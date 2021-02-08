class 'VecLib'
local PI = 3.1415927

function VecLib:__init()
end

function VecLib:Angle(From, To)
    local d_From = From:Dot(To)
    d_From = d_From / (From.magnitude * To.magnitude)
    local arc_Acos = math.acos(d_From)
    return arc_Acos * 180 / PI
end

function VecLib:RandomPointInRadius(Target, Radius)
    return Vec3(
        Target.x + math.random(-Radius, Radius),
        Target.y + math.random(-Radius, Radius),
        Target.z + math.random(-Radius, Radius)
    )
end

function VecLib:CosineInterpolation(x, y, alpha)
    local beta = (1 - math.cos(alpha * math.pi)) / 2
    return (x * (1 - beta) + y * beta)
end

function VecLib:InterpTo(x, y, alpha)
    local newX = self:CosineInterpolation(x.x, y.x, alpha)
    local newY = self:CosineInterpolation(x.y, y.y, alpha)
    local newZ = self:CosineInterpolation(x.z, y.z, alpha)
    return Vec3(newX, newY, newZ)
end

if not g_VecLib then
    g_VecLib = VecLib()
end
return g_VecLib