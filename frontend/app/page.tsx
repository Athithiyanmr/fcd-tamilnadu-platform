'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import AOISelector from '@/components/AOISelector';
import StatsPanel from '@/components/StatsPanel';
import LayerControls from '@/components/LayerControls';

// Load MapLibre client-side only (no SSR)
const FCDMap = dynamic(() => import('@/components